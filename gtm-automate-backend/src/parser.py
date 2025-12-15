"""
Parser Module - Handles JSON and Excel file parsing
Converts input files to standardized format for GTM automation
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Union
import pandas as pd

logger = logging.getLogger(__name__)


class FileParser:
    """Parse JSON and Excel files for GTM automation"""
    
    @staticmethod
    def parse_json(file_path: str) -> Dict:
        """
        Parse JSON input file
        Supports both simple format and GTM Export format
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed data dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✓ Successfully parsed JSON file: {file_path}")
            
            # Check if it's a GTM Export format
            if 'containerVersion' in data:
                logger.info("  Detected GTM Export format - Converting...")
                data = FileParser._convert_gtm_export(data)
                logger.info(f"  ✓ Converted to standard format")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"✗ Invalid JSON format: {str(e)}")
            raise
        except FileNotFoundError:
            logger.error(f"✗ File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"✗ Error parsing JSON: {str(e)}")
            raise
    
    @staticmethod
    def _convert_gtm_export(export_data: Dict) -> Dict:
        """
        Convert GTM Export format to standard format
        
        Args:
            export_data: GTM export JSON data
            
        Returns:
            Standardized data dictionary
        """
        container_version = export_data.get('containerVersion', {})
        
        # Extract tags
        tags_raw = container_version.get('tag', [])
        tags = []
        for tag in tags_raw:
            converted_tag = {
                'name': tag.get('name'),
                'type': tag.get('type'),
                'parameter': []
            }
            
            # Convert parameters
            for param in tag.get('parameter', []):
                converted_tag['parameter'].append({
                    'key': param.get('key'),
                    'type': 'template',
                    'value': param.get('value', '')
                })
            
            # Convert firing triggers (use trigger names instead of IDs)
            if 'firingTriggerId' in tag:
                converted_tag['firingTriggerId'] = FileParser._map_trigger_ids_to_names(
                    tag['firingTriggerId'],
                    container_version.get('trigger', [])
                )
            
            # Convert blocking triggers
            if 'blockingTriggerId' in tag:
                converted_tag['blockingTriggerId'] = FileParser._map_trigger_ids_to_names(
                    tag['blockingTriggerId'],
                    container_version.get('trigger', [])
                )
            
            tags.append(converted_tag)
        
        # Extract triggers
        triggers_raw = container_version.get('trigger', [])
        triggers = []
        for trigger in triggers_raw:
            converted_trigger = {
                'name': trigger.get('name'),
                'type': trigger.get('type')
            }
            
            # Add filters if present
            if 'filter' in trigger:
                converted_trigger['filter'] = trigger['filter']
            
            if 'customEventFilter' in trigger:
                converted_trigger['customEventFilter'] = trigger['customEventFilter']
            
            if 'autoEventFilter' in trigger:
                converted_trigger['autoEventFilter'] = trigger['autoEventFilter']
            
            triggers.append(converted_trigger)
        
        # Extract variables
        variables_raw = container_version.get('variable', [])
        variables = []
        for variable in variables_raw:
            converted_variable = {
                'name': variable.get('name'),
                'type': variable.get('type'),
                'parameter': []
            }
            
            # Convert parameters
            for param in variable.get('parameter', []):
                converted_variable['parameter'].append({
                    'key': param.get('key'),
                    'type': 'template',
                    'value': param.get('value', '')
                })
            
            variables.append(converted_variable)
        
        return {
            'variables': variables,
            'triggers': triggers,
            'tags': tags
        }
    
    @staticmethod
    def _map_trigger_ids_to_names(trigger_ids: List[str], triggers: List[Dict]) -> List[str]:
        """
        Map trigger IDs to trigger names
        
        Args:
            trigger_ids: List of trigger IDs
            triggers: List of trigger objects
            
        Returns:
            List of trigger names
        """
        trigger_map = {t.get('triggerId'): t.get('name') for t in triggers}
        return [trigger_map.get(tid, tid) for tid in trigger_ids]
    
    @staticmethod
    def parse_excel(file_path: str) -> Dict:
        """
        Parse Excel input file
        Expected sheets: Variables, Triggers, Tags
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Parsed data dictionary with standardized structure
        """
        try:
            # Read Excel file
            xl_file = pd.ExcelFile(file_path)
            logger.info(f"✓ Excel file loaded: {file_path}")
            logger.info(f"  Available sheets: {xl_file.sheet_names}")
            
            result = {
                'variables': [],
                'triggers': [],
                'tags': []
            }
            
            # Parse Variables sheet
            if 'Variables' in xl_file.sheet_names:
                df_vars = pd.read_excel(xl_file, sheet_name='Variables')
                result['variables'] = FileParser._parse_variables_sheet(df_vars)
                logger.info(f"  ✓ Parsed {len(result['variables'])} variables")
            
            # Parse Triggers sheet
            if 'Triggers' in xl_file.sheet_names:
                df_triggers = pd.read_excel(xl_file, sheet_name='Triggers')
                result['triggers'] = FileParser._parse_triggers_sheet(df_triggers)
                logger.info(f"  ✓ Parsed {len(result['triggers'])} triggers")
            
            # Parse Tags sheet
            if 'Tags' in xl_file.sheet_names:
                df_tags = pd.read_excel(xl_file, sheet_name='Tags')
                result['tags'] = FileParser._parse_tags_sheet(df_tags)
                logger.info(f"  ✓ Parsed {len(result['tags'])} tags")
            
            return result
            
        except FileNotFoundError:
            logger.error(f"✗ File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"✗ Error parsing Excel: {str(e)}")
            raise

    @staticmethod
    def _parse_variables_sheet(df: pd.DataFrame) -> List[Dict]:
        """
        Parse Variables sheet from Excel
        Expected columns: name, type, value (optional: parameter_key, parameter_value)
        
        Args:
            df: DataFrame from Variables sheet
            
        Returns:
            List of variable dictionaries
        """
        variables = []
        
        for _, row in df.iterrows():
            if pd.isna(row.get('name')):
                continue
            
            variable = {
                'name': str(row['name']),
                'type': str(row.get('type', 'v')),
                'parameter': []
            }
            
            # Handle simple value field
            if 'value' in row and not pd.isna(row['value']):
                variable['parameter'].append({
                    'key': 'value',
                    'type': 'template',
                    'value': str(row['value'])
                })
            
            # Handle custom parameter fields
            if 'parameter_key' in row and not pd.isna(row['parameter_key']):
                param_keys = str(row['parameter_key']).split('|')
                param_values = str(row.get('parameter_value', '')).split('|')
                
                for i, key in enumerate(param_keys):
                    value = param_values[i] if i < len(param_values) else ''
                    variable['parameter'].append({
                        'key': key.strip(),
                        'type': 'template',
                        'value': value.strip()
                    })
            
            variables.append(variable)
        
        return variables
    
    @staticmethod
    def _parse_triggers_sheet(df: pd.DataFrame) -> List[Dict]:
        """
        Parse Triggers sheet from Excel
        Expected columns: name, type, event_name (for custom events), filter_type, filter_parameter
        
        Args:
            df: DataFrame from Triggers sheet
            
        Returns:
            List of trigger dictionaries
        """
        triggers = []
        
        for _, row in df.iterrows():
            if pd.isna(row.get('name')):
                continue
            
            trigger = {
                'name': str(row['name']),
                'type': str(row.get('type', 'PAGEVIEW'))
            }
            
            # Handle custom event triggers
            if trigger['type'] == 'CUSTOM_EVENT' and 'event_name' in row and not pd.isna(row['event_name']):
                trigger['customEventFilter'] = [{
                    'type': 'equals',
                    'parameter': [
                        {'type': 'template', 'key': 'arg0', 'value': '{{_event}}'},
                        {'type': 'template', 'key': 'arg1', 'value': str(row['event_name'])}
                    ]
                }]
            
            # Handle filters
            if 'filter_type' in row and not pd.isna(row['filter_type']):
                trigger['filter'] = [{
                    'type': str(row['filter_type']),
                    'parameter': []
                }]
                
                if 'filter_parameter' in row and not pd.isna(row['filter_parameter']):
                    # Parse filter parameters (format: key1:value1|key2:value2)
                    params = str(row['filter_parameter']).split('|')
                    for param in params:
                        if ':' in param:
                            key, value = param.split(':', 1)
                            trigger['filter'][0]['parameter'].append({
                                'type': 'template',
                                'key': key.strip(),
                                'value': value.strip()
                            })
            
            triggers.append(trigger)
        
        return triggers
    
    @staticmethod
    def _parse_tags_sheet(df: pd.DataFrame) -> List[Dict]:
        """
        Parse Tags sheet from Excel
        Expected columns: name, type, html (for html tags), firing_triggers, blocking_triggers,
                         parameter_key, parameter_value
        
        Args:
            df: DataFrame from Tags sheet
            
        Returns:
            List of tag dictionaries
        """
        tags = []
        
        for _, row in df.iterrows():
            if pd.isna(row.get('name')):
                continue
            
            tag = {
                'name': str(row['name']),
                'type': str(row.get('type', 'html')),
                'parameter': []
            }
            
            # Handle HTML content for html tags
            if tag['type'] == 'html' and 'html' in row and not pd.isna(row['html']):
                tag['parameter'].append({
                    'key': 'html',
                    'type': 'template',
                    'value': str(row['html'])
                })
            
            # Handle custom parameters
            if 'parameter_key' in row and not pd.isna(row['parameter_key']):
                param_keys = str(row['parameter_key']).split('|')
                param_values = str(row.get('parameter_value', '')).split('|')
                
                for i, key in enumerate(param_keys):
                    value = param_values[i] if i < len(param_values) else ''
                    tag['parameter'].append({
                        'key': key.strip(),
                        'type': 'template',
                        'value': value.strip()
                    })
            
            # Handle firing triggers
            if 'firing_triggers' in row and not pd.isna(row['firing_triggers']):
                trigger_names = str(row['firing_triggers']).split('|')
                tag['firingTriggerId'] = [name.strip() for name in trigger_names]
            
            # Handle blocking triggers
            if 'blocking_triggers' in row and not pd.isna(row['blocking_triggers']):
                trigger_names = str(row['blocking_triggers']).split('|')
                tag['blockingTriggerId'] = [name.strip() for name in trigger_names]
            
            tags.append(tag)
        
        return tags
    
    @staticmethod
    def parse_file(file_path: str) -> Dict:
        """
        Auto-detect file type and parse accordingly
        
        Args:
            file_path: Path to input file (JSON or Excel)
            
        Returns:
            Parsed data dictionary
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.json':
            return FileParser.parse_json(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return FileParser.parse_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Use .json, .xlsx, or .xls")
