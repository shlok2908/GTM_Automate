"""
GTM Client - Handles all Google Tag Manager API interactions
Manages authentication, workspace creation, and resource management (variables, triggers, tags)
"""
import logging
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Dict, List, Optional, Any, Tuple
import time

from src.config import Config

logger = logging.getLogger(__name__)


def resolve_account_and_container_by_container_id(
    service_account_file: str,
    target_container: str,
) -> Tuple[str, str]:
    """Resolve GTM accountId and containerId from a container identifier.

    The identifier can be either the numeric container ID (e.g. "237397345")
    or the public ID (e.g. "GTM-XXXXXXX"). This uses the service account
    credentials to list all accounts and containers the service account can
    access, then finds the first matching container.

    Returns:
        (account_id, container_id)

    Raises:
        ValueError: if no matching container is found.
    """
    logger.info("Resolving GTM account/container from container identifier '%s'", target_container)

    try:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=Config.GTM_SCOPES,
        )
        service = build("tagmanager", "v2", credentials=credentials)

        accounts_list = service.accounts().list().execute()
        accounts = accounts_list.get("account", [])

        for account in accounts:
            account_id = account.get("accountId")
            if not account_id:
                continue

            containers_list = service.accounts().containers().list(
                parent=f"accounts/{account_id}"
            ).execute()
            containers = containers_list.get("container", [])

            for container in containers:
                container_id = container.get("containerId")
                public_id = container.get("publicId")

                if target_container == container_id or target_container == public_id:
                    logger.info(
                        "Resolved container '%s' to account %s, container %s",
                        target_container,
                        account_id,
                        container_id,
                    )
                    return account_id, container_id

        raise ValueError(
            f"Could not find GTM container matching identifier '{target_container}'. "
            "Ensure the service account has access to the correct GTM account/container."
        )
    except HttpError as e:
        logger.error("Failed to resolve account/container: %s", e)
        raise


class GTMClient:
    """Google Tag Manager API Client"""
    
    def __init__(self, service_account_file: str, account_id: str, container_id: str):
        """
        Initialize GTM Client
        
        Args:
            service_account_file: Path to service account JSON file
            account_id: GTM Account ID
            container_id: GTM Container ID
        """
        self.account_id = account_id
        self.container_id = container_id
        self.parent = f'accounts/{account_id}/containers/{container_id}'
        self.service = self._authenticate(service_account_file)
        self.workspace_id = None
        self.workspace_path = None
        
    def _authenticate(self, service_account_file: str):
        """
        Authenticate using service account credentials
        
        Args:
            service_account_file: Path to service account JSON file
            
        Returns:
            Authenticated GTM service
        """
        try:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=Config.GTM_SCOPES
            )
            service = build('tagmanager', 'v2', credentials=credentials)
            logger.info("✓ Successfully authenticated with GTM API")
            return service
        except Exception as e:
            logger.error(f"✗ Authentication failed: {str(e)}")
            raise
    
    def create_workspace(self, workspace_name: Optional[str] = None, 
                        description: str = "Auto-generated workspace") -> Dict:
        """
        Create a new GTM workspace
        
        Args:
            workspace_name: Name for the workspace (auto-generated if not provided)
            description: Workspace description
            
        Returns:
            Created workspace object
        """
        try:
            if not workspace_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                workspace_name = f"{Config.WORKSPACE_NAME_PREFIX}_{timestamp}"
            
            workspace_body = {
                'name': workspace_name,
                'description': description
            }
            
            workspace = self.service.accounts().containers().workspaces().create(
                parent=self.parent,
                body=workspace_body
            ).execute()
            
            self.workspace_id = workspace['workspaceId']
            self.workspace_path = workspace['path']
            
            logger.info(f"✓ Workspace created: {workspace['name']} (ID: {self.workspace_id})")
            return workspace
            
        except HttpError as e:
            logger.error(f"✗ Failed to create workspace: {str(e)}")
            raise
    
    def list_workspaces(self) -> List[Dict]:
        """
        List all workspaces in the container
        
        Returns:
            List of workspace objects
        """
        try:
            response = self.service.accounts().containers().workspaces().list(
                parent=self.parent
            ).execute()
            
            workspaces = response.get('workspace', [])
            logger.info(f"Found {len(workspaces)} workspace(s)")
            return workspaces
            
        except HttpError as e:
            logger.error(f"✗ Failed to list workspaces: {str(e)}")
            return []

    def get_or_create_workspace(self, name: str, description: str = "Auto-generated workspace") -> Dict:
        """Get an existing workspace by name or create it if it doesn't exist.

        This allows reusing a fixed workspace (e.g. "Automation Workspace")
        instead of creating a new one on every run.
        """
        # Try to find existing workspace
        workspaces = self.list_workspaces()
        for ws in workspaces:
            if ws.get('name') == name:
                self.workspace_id = ws.get('workspaceId')
                self.workspace_path = ws.get('path')
                logger.info(f" Using existing workspace: {name} (ID: {self.workspace_id})")
                return ws

        # Not found -> create new one
        logger.info(f"Workspace '{name}' not found - creating a new one")
        return self.create_workspace(workspace_name=name, description=description)

    def clear_workspace(self) -> None:
        """Delete all tags, triggers and variables in the current workspace.

        Useful when reusing a single automation workspace so each run starts clean.
        """
        if not self.workspace_path:
            raise ValueError("Workspace not initialized. Call create_workspace() or get_or_create_workspace() first.")

        workspaces_api = self.service.accounts().containers().workspaces()

        # Delete tags first (they depend on triggers/variables)
        try:
            tags_resp = workspaces_api.tags().list(parent=self.workspace_path).execute()
            tags = tags_resp.get('tag', [])
            logger.info(f"Clearing workspace: deleting {len(tags)} tag(s)")
            for tag in tags:
                try:
                    workspaces_api.tags().delete(path=tag['path']).execute()
                    logger.info(f"   Deleted tag: {tag.get('name')} (ID: {tag.get('tagId')})")
                except HttpError as e:
                    logger.warning(f"   Failed to delete tag '{tag.get('name')}': {str(e)}")
        except HttpError as e:
            logger.warning(f"   Failed to list tags for clearing: {str(e)}")

        # Delete triggers
        try:
            triggers_resp = workspaces_api.triggers().list(parent=self.workspace_path).execute()
            triggers = triggers_resp.get('trigger', [])
            logger.info(f"Clearing workspace: deleting {len(triggers)} trigger(s)")
            for trigger in triggers:
                try:
                    workspaces_api.triggers().delete(path=trigger['path']).execute()
                    logger.info(f"   Deleted trigger: {trigger.get('name')} (ID: {trigger.get('triggerId')})")
                except HttpError as e:
                    logger.warning(f"   Failed to delete trigger '{trigger.get('name')}': {str(e)}")
        except HttpError as e:
            logger.warning(f"   Failed to list triggers for clearing: {str(e)}")

        # Delete variables
        try:
            variables_resp = workspaces_api.variables().list(parent=self.workspace_path).execute()
            variables = variables_resp.get('variable', [])
            logger.info(f"Clearing workspace: deleting {len(variables)} variable(s)")
            for variable in variables:
                try:
                    workspaces_api.variables().delete(path=variable['path']).execute()
                    logger.info(f"   Deleted variable: {variable.get('name')} (ID: {variable.get('variableId')})")
                except HttpError as e:
                    logger.warning(f"   Failed to delete variable '{variable.get('name')}': {str(e)}")
        except HttpError as e:
            logger.warning(f"   Failed to list variables for clearing: {str(e)}")
    
    def create_variable(self, variable_data: Dict) -> Dict:
        """
        Create a GTM variable
        
        Args:
            variable_data: Variable configuration dict
                {
                    "name": "Variable Name",
                    "type": "v" (user-defined) or built-in type,
                    "parameter": [{"key": "...", "value": "..."}]
                }
                
        Returns:
            Created variable object
        """
        if not self.workspace_path:
            raise ValueError("Workspace not initialized. Call create_workspace() first.")
        
        try:
            variable_body = {
                'name': variable_data['name'],
                'type': variable_data.get('type', 'v'),
                'parameter': variable_data.get('parameter', [])
            }
            
            variable = self.service.accounts().containers().workspaces().variables().create(
                parent=self.workspace_path,
                body=variable_body
            ).execute()
            
            logger.info(f"  ✓ Variable created: {variable['name']} (ID: {variable['variableId']})")
            return variable
            
        except HttpError as e:
            logger.error(f"  ✗ Failed to create variable '{variable_data.get('name')}': {str(e)}")
            raise
    
    def create_trigger(self, trigger_data: Dict) -> Dict:
        """
        Create a GTM trigger
        
        Args:
            trigger_data: Trigger configuration dict
                {
                    "name": "Trigger Name",
                    "type": "PAGEVIEW" | "CLICK" | "CUSTOM_EVENT" | etc.,
                    "filter": [{"type": "...", "parameter": [...]}]
                }
                
        Returns:
            Created trigger object
        """
        if not self.workspace_path:
            raise ValueError("Workspace not initialized. Call create_workspace() first.")
        
        try:
            trigger_body = {
                'name': trigger_data['name'],
                'type': trigger_data['type']
            }
            
            # Add filters if present
            if 'filter' in trigger_data:
                trigger_body['filter'] = trigger_data['filter']
            
            # Add custom event filter for CUSTOM_EVENT triggers
            if 'customEventFilter' in trigger_data:
                trigger_body['customEventFilter'] = trigger_data['customEventFilter']
            
            # Add auto event filter for click triggers
            if 'autoEventFilter' in trigger_data:
                trigger_body['autoEventFilter'] = trigger_data['autoEventFilter']
            
            trigger = self.service.accounts().containers().workspaces().triggers().create(
                parent=self.workspace_path,
                body=trigger_body
            ).execute()
            
            logger.info(f"  ✓ Trigger created: {trigger['name']} (ID: {trigger['triggerId']})")
            return trigger
            
        except HttpError as e:
            logger.error(f"  ✗ Failed to create trigger '{trigger_data.get('name')}': {str(e)}")
            raise
    
    def create_tag(self, tag_data: Dict, trigger_id_map: Optional[Dict[str, str]] = None) -> Dict:
        """
        Create a GTM tag
        
        Args:
            tag_data: Tag configuration dict
                {
                    "name": "Tag Name",
                    "type": "html" | "ua" | "img" | etc.,
                    "parameter": [{"key": "...", "value": "..."}],
                    "firingTriggerId": ["trigger_name_1", "trigger_name_2"],
                    "blockingTriggerId": ["blocking_trigger_name"]
                }
            trigger_id_map: Mapping of trigger names to trigger IDs
                
        Returns:
            Created tag object
        """
        if not self.workspace_path:
            raise ValueError("Workspace not initialized. Call create_workspace() first.")
        
        try:
            tag_body = {
                'name': tag_data['name'],
                'type': tag_data['type'],
                'parameter': tag_data.get('parameter', [])
            }
            
            # Map firing trigger names to IDs
            if 'firingTriggerId' in tag_data and trigger_id_map:
                firing_trigger_ids = []
                for trigger_name in tag_data['firingTriggerId']:
                    if trigger_name in trigger_id_map:
                        firing_trigger_ids.append(trigger_id_map[trigger_name])
                    else:
                        logger.warning(f"  ⚠ Firing trigger '{trigger_name}' not found in trigger map")
                
                tag_body['firingTriggerId'] = firing_trigger_ids
            
            # Map blocking trigger names to IDs
            if 'blockingTriggerId' in tag_data and trigger_id_map:
                blocking_trigger_ids = []
                for trigger_name in tag_data['blockingTriggerId']:
                    if trigger_name in trigger_id_map:
                        blocking_trigger_ids.append(trigger_id_map[trigger_name])
                    else:
                        logger.warning(f"  ⚠ Blocking trigger '{trigger_name}' not found in trigger map")
                
                tag_body['blockingTriggerId'] = blocking_trigger_ids
            
            tag = self.service.accounts().containers().workspaces().tags().create(
                parent=self.workspace_path,
                body=tag_body
            ).execute()
            
            logger.info(f"  ✓ Tag created: {tag['name']} (ID: {tag['tagId']})")
            return tag
            
        except HttpError as e:
            logger.error(f"  ✗ Failed to create tag '{tag_data.get('name')}': {str(e)}")
            raise
    
    def get_workspace_url(self) -> str:
        """
        Get the GTM web UI URL for the current workspace
        
        Returns:
            URL string
        """
        if not self.workspace_id:
            return ""
        
        return (f"https://tagmanager.google.com/#/container/"
                f"accounts/{self.account_id}/containers/{self.container_id}/"
                f"workspaces/{self.workspace_id}")
