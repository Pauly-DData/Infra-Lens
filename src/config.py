"""
Configuration management for CDK Diff Summarizer.
Handles all configuration options, validation, and defaults.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class OutputFormat(Enum):
    """Supported output formats."""
    COMMENT = "comment"
    ISSUE = "issue"
    BOTH = "both"
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


class Language(Enum):
    """Supported languages."""
    EN = "en"
    NL = "nl"
    DE = "de"
    FR = "fr"
    ES = "es"


@dataclass
class AIConfig:
    """AI service configuration."""
    api_key: str
    model: str = "gpt-4"
    max_tokens: int = 500
    temperature: float = 0.7
    max_retries: int = 3
    timeout: int = 30
    base_url: Optional[str] = None


@dataclass
class GitHubConfig:
    """GitHub integration configuration."""
    token: str
    repository: str
    event_path: str
    output_path: str = field(default_factory=lambda: os.getenv('GITHUB_OUTPUT', '/dev/null'))
    create_issue_if_no_pr: bool = False


@dataclass
class TemplateConfig:
    """Template configuration."""
    template_path: Optional[str] = None
    language: Language = Language.EN
    custom_variables: Dict[str, str] = field(default_factory=dict)


@dataclass
class CacheConfig:
    """Caching configuration."""
    enabled: bool = True
    cache_dir: str = ".infra-lens-cache"
    ttl_hours: int = 24
    max_cache_size_mb: int = 100


@dataclass
class Config:
    """Main configuration class."""
    # Core settings
    cdk_diff_file: str = "cdk-diff.json"
    output_format: OutputFormat = OutputFormat.BOTH
    working_directory: str = "."
    
    # Service configurations
    ai: AIConfig = field(default_factory=lambda: AIConfig(api_key=""))
    github: Optional[GitHubConfig] = None
    template: TemplateConfig = field(default_factory=TemplateConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    # Feature flags
    enable_metadata: bool = True
    enable_validation: bool = True
    enable_logging: bool = True
    enable_metrics: bool = False
    
    # Advanced settings
    log_level: str = "INFO"
    dry_run: bool = False
    
    def __post_init__(self):
        """Validate and set defaults after initialization."""
        self._load_from_environment()
        self._validate()
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # AI Configuration
        if not self.ai.api_key:
            self.ai.api_key = os.getenv('OPENAI_API_KEY', '')
        
        self.ai.model = os.getenv('AI_MODEL', self.ai.model)
        self.ai.max_tokens = int(os.getenv('AI_MAX_TOKENS', str(self.ai.max_tokens)))
        self.ai.temperature = float(os.getenv('AI_TEMPERATURE', str(self.ai.temperature)))
        self.ai.max_retries = int(os.getenv('AI_MAX_RETRIES', str(self.ai.max_retries)))
        self.ai.timeout = int(os.getenv('AI_TIMEOUT', str(self.ai.timeout)))
        self.ai.base_url = os.getenv('AI_BASE_URL', self.ai.base_url)
        
        # Core settings
        self.cdk_diff_file = os.getenv('CDK_DIFF_FILE', self.cdk_diff_file)
        self.output_format = OutputFormat(os.getenv('OUTPUT_FORMAT', self.output_format.value))
        self.working_directory = os.getenv('WORKING_DIRECTORY', self.working_directory)
        
        # GitHub Configuration
        github_token = os.getenv('GITHUB_TOKEN')
        github_repo = os.getenv('GITHUB_REPOSITORY')
        github_event_path = os.getenv('GITHUB_EVENT_PATH')
        
        if github_token and github_repo and github_event_path:
            self.github = GitHubConfig(
                token=github_token,
                repository=github_repo,
                event_path=github_event_path,
                create_issue_if_no_pr=os.getenv('CREATE_ISSUE_IF_NO_PR', 'false').lower() == 'true'
            )
        
        # Template Configuration
        template_path = os.getenv('TEMPLATE_PATH')
        if template_path:
            self.template.template_path = template_path
        
        language = os.getenv('LANGUAGE', 'en')
        try:
            self.template.language = Language(language)
        except ValueError:
            self.template.language = Language.EN
        
        # Cache Configuration
        self.cache.enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        self.cache.cache_dir = os.getenv('CACHE_DIR', self.cache.cache_dir)
        self.cache.ttl_hours = int(os.getenv('CACHE_TTL_HOURS', str(self.cache.ttl_hours)))
        self.cache.max_cache_size_mb = int(os.getenv('CACHE_MAX_SIZE_MB', str(self.cache.max_cache_size_mb)))
        
        # Feature flags
        self.enable_metadata = os.getenv('ENABLE_METADATA', 'true').lower() == 'true'
        self.enable_validation = os.getenv('ENABLE_VALIDATION', 'true').lower() == 'true'
        self.enable_logging = os.getenv('ENABLE_LOGGING', 'true').lower() == 'true'
        self.enable_metrics = os.getenv('ENABLE_METRICS', 'false').lower() == 'true'
        
        # Advanced settings
        self.log_level = os.getenv('LOG_LEVEL', self.log_level)
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
    
    def _validate(self):
        """Validate configuration values."""
        if not self.ai.api_key:
            raise ValueError("AI API key is required")
        
        if self.ai.max_tokens <= 0:
            raise ValueError("AI max_tokens must be positive")
        
        if not (0 <= self.ai.temperature <= 2):
            raise ValueError("AI temperature must be between 0 and 2")
        
        if self.ai.max_retries < 0:
            raise ValueError("AI max_retries must be non-negative")
        
        if self.cache.ttl_hours <= 0:
            raise ValueError("Cache TTL must be positive")
        
        if self.cache.max_cache_size_mb <= 0:
            raise ValueError("Cache max size must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'cdk_diff_file': self.cdk_diff_file,
            'output_format': self.output_format.value,
            'working_directory': self.working_directory,
            'ai': {
                'model': self.ai.model,
                'max_tokens': self.ai.max_tokens,
                'temperature': self.ai.temperature,
                'max_retries': self.ai.max_retries,
                'timeout': self.ai.timeout,
                'base_url': self.ai.base_url
            },
            'github': {
                'repository': self.github.repository if self.github else None,
                'create_issue_if_no_pr': self.github.create_issue_if_no_pr if self.github else False
            },
            'template': {
                'template_path': self.template.template_path,
                'language': self.template.language.value,
                'custom_variables': self.template.custom_variables
            },
            'cache': {
                'enabled': self.cache.enabled,
                'cache_dir': self.cache.cache_dir,
                'ttl_hours': self.cache.ttl_hours,
                'max_cache_size_mb': self.cache.max_cache_size_mb
            },
            'features': {
                'enable_metadata': self.enable_metadata,
                'enable_validation': self.enable_validation,
                'enable_logging': self.enable_logging,
                'enable_metrics': self.enable_metrics
            },
            'advanced': {
                'log_level': self.log_level,
                'dry_run': self.dry_run
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create configuration from dictionary."""
        config = cls()
        
        # Update core settings
        if 'cdk_diff_file' in data:
            config.cdk_diff_file = data['cdk_diff_file']
        if 'output_format' in data:
            config.output_format = OutputFormat(data['output_format'])
        if 'working_directory' in data:
            config.working_directory = data['working_directory']
        
        # Update AI config
        if 'ai' in data:
            ai_data = data['ai']
            config.ai.model = ai_data.get('model', config.ai.model)
            config.ai.max_tokens = ai_data.get('max_tokens', config.ai.max_tokens)
            config.ai.temperature = ai_data.get('temperature', config.ai.temperature)
            config.ai.max_retries = ai_data.get('max_retries', config.ai.max_retries)
            config.ai.timeout = ai_data.get('timeout', config.ai.timeout)
            config.ai.base_url = ai_data.get('base_url', config.ai.base_url)
        
        # Update template config
        if 'template' in data:
            template_data = data['template']
            config.template.template_path = template_data.get('template_path')
            if 'language' in template_data:
                config.template.language = Language(template_data['language'])
            config.template.custom_variables = template_data.get('custom_variables', {})
        
        # Update cache config
        if 'cache' in data:
            cache_data = data['cache']
            config.cache.enabled = cache_data.get('enabled', config.cache.enabled)
            config.cache.cache_dir = cache_data.get('cache_dir', config.cache.cache_dir)
            config.cache.ttl_hours = cache_data.get('ttl_hours', config.cache.ttl_hours)
            config.cache.max_cache_size_mb = cache_data.get('max_cache_size_mb', config.cache.max_cache_size_mb)
        
        # Update feature flags
        if 'features' in data:
            features_data = data['features']
            config.enable_metadata = features_data.get('enable_metadata', config.enable_metadata)
            config.enable_validation = features_data.get('enable_validation', config.enable_validation)
            config.enable_logging = features_data.get('enable_logging', config.enable_logging)
            config.enable_metrics = features_data.get('enable_metrics', config.enable_metrics)
        
        # Update advanced settings
        if 'advanced' in data:
            advanced_data = data['advanced']
            config.log_level = advanced_data.get('log_level', config.log_level)
            config.dry_run = advanced_data.get('dry_run', config.dry_run)
        
        return config 