"""
Template system for CDK Diff Summarizer.
Handles template loading, rendering, and localization.
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from config import Language, Config


class TemplateManager:
    """Manages template loading and rendering."""
    
    def __init__(self, config: Config):
        self.config = config
        self.env = self._setup_jinja_environment()
        self.templates = self._load_templates()
    
    def _setup_jinja_environment(self) -> Environment:
        """Setup Jinja2 environment with custom filters and functions."""
        # Determine template search paths
        search_paths = []
        
        # Custom template path from config
        if self.config.template.template_path:
            search_paths.append(self.config.template.template_path)
        
        # Built-in templates directory
        builtin_templates = Path(__file__).parent.parent / "templates"
        if builtin_templates.exists():
            search_paths.append(str(builtin_templates))
        
        # Current working directory
        search_paths.append(self.config.working_directory)
        
        env = Environment(
            loader=FileSystemLoader(search_paths),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        env.filters['format_resource_type'] = self._format_resource_type
        env.filters['format_action'] = self._format_action
        env.filters['format_cost'] = self._format_cost
        env.filters['format_risk_level'] = self._format_risk_level
        
        # Add custom functions
        env.globals['get_language_text'] = self._get_language_text
        
        return env
    
    def _load_templates(self) -> Dict[str, Template]:
        """Load all available templates."""
        templates = {}
        
        # Load built-in templates
        builtin_templates = Path(__file__).parent.parent / "templates"
        if builtin_templates.exists():
            for template_file in builtin_templates.glob("*.md"):
                template_name = template_file.stem
                try:
                    template = self.env.get_template(template_file.name)
                    templates[template_name] = template
                except Exception as e:
                    print(f"Warning: Failed to load template {template_name}: {e}")
        
        # Load custom template if specified
        if self.config.template.template_path:
            custom_template_path = Path(self.config.template.template_path)
            if custom_template_path.exists():
                try:
                    template_name = custom_template_path.stem
                    template = self.env.get_template(custom_template_path.name)
                    templates[template_name] = template
                except Exception as e:
                    print(f"Warning: Failed to load custom template: {e}")
        
        return templates
    
    def render_summary(self, diff_data: Dict[str, Any], format_type: str = "default") -> str:
        """Render summary using the appropriate template."""
        # Get template based on format and language
        template_name = self._get_template_name(format_type)
        
        if template_name not in self.templates:
            # Fallback to default template
            template_name = "default"
            if template_name not in self.templates:
                raise ValueError("No templates available")
        
        template = self.templates[template_name]
        
        # Prepare template context
        context = self._prepare_context(diff_data)
        
        # Render template
        return template.render(**context)
    
    def _get_template_name(self, format_type: str) -> str:
        """Get template name based on format and language."""
        language = self.config.template.language.value
        
        # Try language-specific template first
        template_name = f"{format_type}_{language}"
        if template_name in self.templates:
            return template_name
        
        # Fallback to format-specific template
        if format_type in self.templates:
            return format_type
        
        # Fallback to default
        return "default"
    
    def _prepare_context(self, diff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context data for template rendering."""
        # Extract changes from diff data
        changes = self._extract_changes(diff_data)
        
        # Calculate statistics
        stats = self._calculate_statistics(changes)
        
        # Prepare context
        context = {
            'changes': changes,
            'statistics': stats,
            'language': self.config.template.language.value,
            'config': self.config.to_dict(),
            'custom_variables': self.config.template.custom_variables,
            'metadata': {
                'generator': 'CDK Diff Summarizer',
                'version': '1.0.0',
                'model': self.config.ai.model,
                'timestamp': self._get_timestamp()
            }
        }
        
        return context
    
    def _extract_changes(self, diff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and organize changes from CDK diff data."""
        changes = {
            'stacks': [],
            'resources': [],
            'summary': {
                'total_changes': 0,
                'creates': 0,
                'updates': 0,
                'deletes': 0,
                'replaces': 0
            }
        }
        
        stacks_data = diff_data.get('stacks', {})
        
        for stack_name, stack_data in stacks_data.items():
            stack_changes = {
                'name': stack_name,
                'actions': [],
                'resources': []
            }
            
            # Stack-level changes
            if stack_data.get('create'):
                stack_changes['actions'].append('create')
                changes['summary']['creates'] += 1
            if stack_data.get('update'):
                stack_changes['actions'].append('update')
                changes['summary']['updates'] += 1
            if stack_data.get('destroy'):
                stack_changes['actions'].append('destroy')
                changes['summary']['deletes'] += 1
            
            # Resource changes
            resources_data = stack_data.get('resources', {})
            for resource_id, resource_data in resources_data.items():
                resource_change = {
                    'id': resource_id,
                    'type': resource_data.get('type', 'Unknown'),
                    'stack': stack_name,
                    'actions': []
                }
                
                if resource_data.get('create'):
                    resource_change['actions'].append('create')
                    changes['summary']['creates'] += 1
                if resource_data.get('update'):
                    resource_change['actions'].append('update')
                    changes['summary']['updates'] += 1
                if resource_data.get('destroy'):
                    resource_change['actions'].append('destroy')
                    changes['summary']['deletes'] += 1
                if resource_data.get('replace'):
                    resource_change['actions'].append('replace')
                    changes['summary']['replaces'] += 1
                
                if resource_change['actions']:
                    stack_changes['resources'].append(resource_change)
                    changes['resources'].append(resource_change)
            
            if stack_changes['actions'] or stack_changes['resources']:
                changes['stacks'].append(stack_changes)
        
        changes['summary']['total_changes'] = (
            changes['summary']['creates'] +
            changes['summary']['updates'] +
            changes['summary']['deletes'] +
            changes['summary']['replaces']
        )
        
        return changes
    
    def _calculate_statistics(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics from changes."""
        stats = {
            'total_stacks': len(changes['stacks']),
            'total_resources': len(changes['resources']),
            'resource_types': {},
            'risk_level': 'low',
            'estimated_cost_impact': 'minimal'
        }
        
        # Count resource types
        for resource in changes['resources']:
            resource_type = resource['type']
            if resource_type not in stats['resource_types']:
                stats['resource_types'][resource_type] = 0
            stats['resource_types'][resource_type] += 1
        
        # Determine risk level
        high_risk_types = {'AWS::IAM::', 'AWS::KMS::', 'AWS::SecretsManager::'}
        medium_risk_types = {'AWS::EC2::', 'AWS::RDS::', 'AWS::Lambda::'}
        
        risk_score = 0
        for resource in changes['resources']:
            resource_type = resource['type']
            if any(high_risk in resource_type for high_risk in high_risk_types):
                risk_score += 3
            elif any(medium_risk in resource_type for medium_risk in medium_risk_types):
                risk_score += 2
            else:
                risk_score += 1
        
        if risk_score > 10:
            stats['risk_level'] = 'high'
        elif risk_score > 5:
            stats['risk_level'] = 'medium'
        else:
            stats['risk_level'] = 'low'
        
        # Estimate cost impact
        total_changes = changes['summary']['total_changes']
        if total_changes > 20:
            stats['estimated_cost_impact'] = 'significant'
        elif total_changes > 10:
            stats['estimated_cost_impact'] = 'moderate'
        else:
            stats['estimated_cost_impact'] = 'minimal'
        
        return stats
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    # Custom Jinja2 filters
    def _format_resource_type(self, resource_type: str) -> str:
        """Format resource type for display."""
        # Remove AWS:: prefix and format nicely
        if resource_type.startswith('AWS::'):
            return resource_type[5:].replace('::', ' ')
        return resource_type
    
    def _format_action(self, action: str) -> str:
        """Format action for display."""
        action_map = {
            'create': '➕ Create',
            'update': '🔄 Update',
            'destroy': '🗑️ Delete',
            'replace': '🔄 Replace'
        }
        return action_map.get(action, action.title())
    
    def _format_cost(self, cost_impact: str) -> str:
        """Format cost impact for display."""
        cost_map = {
            'minimal': '💰 Minimal',
            'moderate': '💰💰 Moderate',
            'significant': '💰💰💰 Significant'
        }
        return cost_map.get(cost_impact, cost_impact.title())
    
    def _format_risk_level(self, risk_level: str) -> str:
        """Format risk level for display."""
        risk_map = {
            'low': '🟢 Low Risk',
            'medium': '🟡 Medium Risk',
            'high': '🔴 High Risk'
        }
        return risk_map.get(risk_level, risk_level.title())
    
    def _get_language_text(self, key: str, language: str = None) -> str:
        """Get localized text for the given key."""
        if language is None:
            language = self.config.template.language.value
        
        # Language-specific text mappings
        texts = {
            'en': {
                'executive_summary': 'Executive Summary',
                'resource_changes': 'Resource Changes',
                'security_considerations': 'Security Considerations',
                'cost_impact': 'Cost Impact',
                'risk_assessment': 'Risk Assessment',
                'deployment_notes': 'Deployment Notes',
                'no_changes': 'No infrastructure changes detected',
                'created': 'Created',
                'updated': 'Updated',
                'deleted': 'Deleted',
                'replaced': 'Replaced'
            },
            'nl': {
                'executive_summary': 'Uitvoerende Samenvatting',
                'resource_changes': 'Resource Wijzigingen',
                'security_considerations': 'Beveiligingsoverwegingen',
                'cost_impact': 'Kostenimpact',
                'risk_assessment': 'Risicobeoordeling',
                'deployment_notes': 'Deployment Notities',
                'no_changes': 'Geen infrastructuurwijzigingen gedetecteerd',
                'created': 'Aangemaakt',
                'updated': 'Bijgewerkt',
                'deleted': 'Verwijderd',
                'replaced': 'Vervangen'
            }
        }
        
        return texts.get(language, texts['en']).get(key, key)
    
    def _format_action(self, action: str) -> str:
        """Format action for display."""
        language = self.config.template.language.value
        
        if language == 'nl':
            action_map = {
                'create': '➕ Aanmaken',
                'update': '🔄 Bijwerken',
                'destroy': '🗑️ Verwijderen',
                'replace': '🔄 Vervangen'
            }
        else:
            action_map = {
                'create': '➕ Create',
                'update': '🔄 Update',
                'destroy': '🗑️ Delete',
                'replace': '🔄 Replace'
            }
        
        return action_map.get(action, action.title())
    
    def _format_cost(self, cost_impact: str) -> str:
        """Format cost impact for display."""
        language = self.config.template.language.value
        
        if language == 'nl':
            cost_map = {
                'minimal': '💰 Minimaal',
                'moderate': '💰💰 Gemiddeld',
                'significant': '💰💰💰 Significant'
            }
        else:
            cost_map = {
                'minimal': '💰 Minimal',
                'moderate': '💰💰 Moderate',
                'significant': '💰💰💰 Significant'
            }
        
        return cost_map.get(cost_impact, cost_impact.title())
    
    def _format_risk_level(self, risk_level: str) -> str:
        """Format risk level for display."""
        language = self.config.template.language.value
        
        if language == 'nl':
            risk_map = {
                'low': '🟢 Laag Risico',
                'medium': '🟡 Gemiddeld Risico',
                'high': '🔴 Hoog Risico'
            }
        else:
            risk_map = {
                'low': '🟢 Low Risk',
                'medium': '🟡 Medium Risk',
                'high': '🔴 High Risk'
            }
        
        return risk_map.get(risk_level, risk_level.title()) 