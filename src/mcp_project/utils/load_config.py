import json
import os
from dotenv import load_dotenv


def load_api_config(api_config_path: str = "config/api_config.json") -> dict:
        """
        Load API configuration file
        
        Returns:
            dict: API configuration dictionary
        """
        load_dotenv()
        # Default configuration
        default_config = {
            "openai_api": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1"),
                "model_name": os.getenv("OPENAI_MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct"),
                "parameters": {
                    "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                    "top_p": float(os.getenv("OPENAI_TOP_P", "1.0")),
                    "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
                    "tool_choice": os.getenv("OPENAI_TOOL_CHOICE", "auto")
                }
            }
        }
        
        try:
            if os.path.exists(api_config_path):
                with open(api_config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    
                    # If API key is empty in configuration, use environment variable
                    if not config.get("openai_api", {}).get("api_key"):
                        config["openai_api"]["api_key"] = os.getenv("OPENAI_API_KEY", "")
                    
                    return config
            else:
                print(f"Warning: API configuration file {api_config_path} does not exist, will use environment variables or default settings")
                return default_config
                
        except Exception as e:
            print(f"Error loading API configuration file: {str(e)}, will use environment variables or default settings")
            return default_config