"""
GTM Automation - Main Application Entry Point
Orchestrates the entire workflow from file parsing to GTM workspace creation
"""
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
import time

from src.config import Config
from src.gtm_client import GTMClient, resolve_account_and_container_by_container_id
from src.parser import FileParser
from src.schema import validate_all
from src.utils.helpers import setup_logging, format_summary, validate_file_path, create_trigger_id_map

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Automate GTM workspace creation with variables, triggers, and tags'
    )
    
    parser.add_argument(
        '--input',
        '-i',
        required=True,
        help='Path to input file (JSON or Excel)'
    )

    parser.add_argument(
        '--account-id',
        help='Optional GTM Account ID (overrides GTM_ACCOUNT_ID from .env)'
    )

    parser.add_argument(
        '--container-id',
        help=(
            'Optional GTM Container identifier. Can be numeric containerId '
            '(e.g. "237397345") or public ID (e.g. "GTM-XXXXXXX"). '
            'If account ID is not provided, it will be auto-resolved.'
        ),
    )
    
    parser.add_argument(
        '--workspace',
        '-w',
        help='Custom workspace name (default: auto-generated with timestamp)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate input without creating GTM resources'
    )

    parser.add_argument(
        '--template-type',
        help='Only upload items of this template type (e.g. html, custom, etc.)',
        required=False
    )
    return parser.parse_args()


def main():
    """Main execution function"""
    start_time = time.time()
    args = parse_arguments()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else Config.LOG_LEVEL
    setup_logging(log_level=log_level, log_file=Config.LOG_FILE)
    
    logger.info("="*70)
    logger.info("  GTM AUTOMATION - STARTING")
    logger.info("="*70)
    
    stats = {
        'workspace_name': None,
        'workspace_id': None,
        'workspace_url': None,
        'variables_created': 0,
        'triggers_created': 0,
        'tags_created': 0,
        'errors': [],
        'status': 'FAILED',
        'duration': None
    }
    
    try:
        # Step 1: Validate configuration
        logger.info("\n[Step 1/7] Validating configuration...")
        # Only require that the service account exists here; account/container
        # can be provided via CLI or resolved from container ID.
        Config.validate(require_account_id=False, require_container_id=False)
        logger.info("✓ Configuration validated")

        # Step 2: Validate and parse input file
        logger.info("\n[Step 2/7] Reading input file...")
        validate_file_path(args.input, allowed_extensions={'.json', '.xlsx', '.xls'})
        data = FileParser.parse_file(args.input)
        logger.info(f"✓ Input file parsed successfully")
        logger.info(f"  - Variables: {len(data.get('variables', []))}")
        logger.info(f"  - Triggers: {len(data.get('triggers', []))}")
        logger.info(f"  - Tags: {len(data.get('tags', []))}")

        # Filter by template type if provided
        if args.template_type:
            logger.info(f"Filtering all items by template type: {args.template_type}")
            data['variables'] = [v for v in data.get('variables', []) if v.get('type') == args.template_type]
            data['triggers'] = [t for t in data.get('triggers', []) if t.get('type') == args.template_type]
            data['tags'] = [tg for tg in data.get('tags', []) if tg.get('type') == args.template_type]
            logger.info(f"  - Variables after filter: {len(data.get('variables', []))}")
            logger.info(f"  - Triggers after filter: {len(data.get('triggers', []))}")
            logger.info(f"  - Tags after filter: {len(data.get('tags', []))}")

        # Step 3: Validate data schema
        logger.info("\n[Step 3/7] Validating data schema...")
        validate_all(data)
        logger.info("✓ Data validation passed")

        # If dry-run, stop here
        if args.dry_run:
            logger.info("\n✓ DRY RUN COMPLETED - No GTM resources created")
            stats['status'] = 'DRY_RUN_SUCCESS'
            print(format_summary(stats))
            return 0
        
        # Step 4: Resolve account/container and authenticate with GTM
        logger.info("\n[Step 4/7] Resolving GTM account and container...")

        # Prefer CLI values, then fall back to environment variables (if set)
        account_id = args.account_id or Config.GTM_ACCOUNT_ID or None
        container_id = args.container_id or Config.GTM_CONTAINER_ID or None

        if not container_id:
            raise ValueError(
                "No GTM container ID provided. Pass --container-id (numeric ID "
                "or GTM-XXXX public ID), or supply it via the UI."
            )

        if not account_id:
            logger.info(
                "No GTM account ID provided; attempting to resolve from container '%s'",
                container_id,
            )
            account_id, container_id = resolve_account_and_container_by_container_id(
                Config.SERVICE_ACCOUNT_JSON_PATH,
                container_id,
            )

        logger.info(
            "Using GTM Account ID: %s, Container ID: %s", account_id, container_id
        )

        logger.info("\n[Step 4/7] Authenticating with GTM API...")
        gtm_client = GTMClient(
            service_account_file=Config.SERVICE_ACCOUNT_JSON_PATH,
            account_id=account_id,
            container_id=container_id,
        )
        
        # Step 5: Get or create fixed automation workspace and clear it
        logger.info("\n[Step 5/7] Preparing GTM workspace...")
        workspace_name = args.workspace or "Automation Workspace"
        workspace = gtm_client.get_or_create_workspace(
            name=workspace_name,
            description=f"Automation workspace for {Path(args.input).name}"
        )
        logger.info("\n  Clearing existing resources in workspace '%s'...", workspace_name)
        gtm_client.clear_workspace()
        stats['workspace_name'] = workspace['name']
        stats['workspace_id'] = workspace['workspaceId']
        stats['workspace_url'] = gtm_client.get_workspace_url()
        
        # Step 6: Create resources
        logger.info("\n[Step 6/7] Creating GTM resources...")
        
        # Create Variables
        logger.info(f"\n  Creating {len(data['variables'])} variable(s)...")
        for variable_data in data['variables']:
            try:
                gtm_client.create_variable(variable_data)
                stats['variables_created'] += 1
            except Exception as e:
                error_msg = f"Failed to create variable '{variable_data.get('name')}': {str(e)}"
                logger.error(f"  ✗ {error_msg}")
                stats['errors'].append(error_msg)
        
        # Create Triggers and build ID map
        logger.info(f"\n  Creating {len(data['triggers'])} trigger(s)...")
        trigger_id_map = {}
        created_triggers = []
        for trigger_data in data['triggers']:
            try:
                trigger = gtm_client.create_trigger(trigger_data)
                created_triggers.append(trigger)
                trigger_id_map[trigger['name']] = trigger['triggerId']
                stats['triggers_created'] += 1
            except Exception as e:
                error_msg = f"Failed to create trigger '{trigger_data.get('name')}': {str(e)}"
                logger.error(f"  ✗ {error_msg}")
                stats['errors'].append(error_msg)
        
        # Create Tags
        logger.info(f"\n  Creating {len(data['tags'])} tag(s)...")
        for tag_data in data['tags']:
            try:
                gtm_client.create_tag(tag_data, trigger_id_map)
                stats['tags_created'] += 1
            except Exception as e:
                error_msg = f"Failed to create tag '{tag_data.get('name')}': {str(e)}"
                logger.error(f"  ✗ {error_msg}")
                stats['errors'].append(error_msg)
        
        # Step 7: Complete
        logger.info("\n[Step 7/7] Finalizing...")
        
        # Determine status
        total_expected = len(data['variables']) + len(data['triggers']) + len(data['tags'])
        total_created = stats['variables_created'] + stats['triggers_created'] + stats['tags_created']
        
        if total_created == total_expected and not stats['errors']:
            stats['status'] = 'SUCCESS'
        elif total_created > 0:
            stats['status'] = 'PARTIAL_SUCCESS'
        else:
            stats['status'] = 'FAILED'
        
        # Calculate duration
        duration_seconds = time.time() - start_time
        stats['duration'] = f"{duration_seconds:.2f}s"
        
        # Print summary
        print("\n" + format_summary(stats))
        
        if stats['status'] == 'SUCCESS':
            logger.info("✓ GTM AUTOMATION COMPLETED SUCCESSFULLY")
            logger.info(f"\n🔗 Open GTM Workspace: {stats['workspace_url']}")
            logger.info("\n➡️  Next Step: Review the workspace and click 'Submit' in GTM UI")
            return 0
        elif stats['status'] == 'PARTIAL_SUCCESS':
            logger.warning("⚠ GTM AUTOMATION COMPLETED WITH ERRORS")
            logger.warning(f"  {len(stats['errors'])} error(s) occurred")
            return 1
        else:
            logger.error("✗ GTM AUTOMATION FAILED")
            return 1
            
    except KeyboardInterrupt:
        logger.error("\n✗ Process interrupted by user")
        stats['status'] = 'INTERRUPTED'
        return 130
        
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {str(e)}", exc_info=args.verbose)
        stats['errors'].append(str(e))
        stats['status'] = 'FAILED'
        
        # Calculate duration
        duration_seconds = time.time() - start_time
        stats['duration'] = f"{duration_seconds:.2f}s"
        
        print("\n" + format_summary(stats))
        return 1


if __name__ == '__main__':
    sys.exit(main())
