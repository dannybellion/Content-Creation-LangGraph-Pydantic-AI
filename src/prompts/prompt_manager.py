from pathlib import Path
from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateError,
    meta,
)


class PromptManager:
    _envs = {}

    @classmethod
    def _get_env(cls, templates_dir="prompts/templates"):
        templates_dir = Path(__file__).parent.parent / templates_dir
        if not templates_dir.exists():
            raise ValueError(f"Templates directory not found: {templates_dir}")
        if templates_dir not in cls._envs:
            cls._envs[templates_dir] = Environment(
                loader=FileSystemLoader(templates_dir),
                undefined=StrictUndefined,
            )
        return cls._envs[templates_dir]

    @staticmethod
    def get_prompt(template, **kwargs):
        env = PromptManager._get_env()
        template_path = f"{template}.j2"
        try:
            template_content = env.loader.get_source(env, template_path)[0]
            return env.from_string(template_content).render(**kwargs)
        except TemplateError as e:
            templates_dir = Path(env.loader.searchpath[0])
            available_templates = list(templates_dir.glob("*.j2"))

            if "is undefined" in str(e):
                template_info = PromptManager.get_template_info(template)
                required_vars = template_info["variables"]
                provided_vars = list(kwargs.keys())
                missing_vars = [
                    var for var in required_vars if var not in provided_vars
                ]
                error_msg = (
                    f"Error rendering template: {str(e)}. "
                    f"Required variables: {required_vars}. "
                    f"Missing variables: {missing_vars}. "
                )
            else:
                error_msg = f"Error rendering template: {str(e)}. "
                error_msg += f"Available templates: {available_templates}"

            raise ValueError(error_msg)

    @staticmethod
    def get_sql_query(query_name, **kwargs):
        env = PromptManager._get_env("prompts/sql")
        query_path = f"{query_name}.sql"
        try:
            query_content = env.loader.get_source(env, query_path)[0]
            template = env.from_string(query_content)
            return template.render(**kwargs)
        except TemplateError as e:
            raise ValueError(f"Error rendering SQL query: {str(e)}")

    @staticmethod
    def get_template_info(template):
        env = PromptManager._get_env()
        template_path = f"{template}.j2"
        try:
            template_content = env.loader.get_source(env, template_path)[0]
            ast = env.parse(template_content)
            variables = meta.find_undeclared_variables(ast)
            return {
                "name": template,
                "variables": list(variables),
            }
        except Exception as e:
            raise ValueError(f"Error getting template info: {str(e)}")
