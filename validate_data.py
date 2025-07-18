import argparse
import sys
from pathlib import Path

import datasets as hfds
from loguru import logger
from openai.types.chat import ChatCompletionMessageParam
from pydantic import TypeAdapter, ValidationError

from config import load_config_for_validation





def validate_input_data_format(ds, input_column_name: str, id_column_name: str, api_type: str):
    """Validate that the input data format matches the expected API type format"""
    if len(ds) == 0:
        logger.warning("Empty dataset, skipping format validation")
        return
    
    # Sample a few rows to check format (up to 10 rows)
    sample_size = min(10, len(ds))
    sample_rows = ds.select(range(sample_size))
    
    for i, row in enumerate(sample_rows):
        if input_column_name not in row:
            raise ValueError(f"Column '{input_column_name}' not found in dataset. Available columns: {list(row.keys())}")
        
        if id_column_name not in row:
            raise ValueError(f"Column '{id_column_name}' not found in dataset. Available columns: {list(row.keys())}")
        
        data = row[input_column_name]
        row_id = row[id_column_name]
        
        # Validate that ID is a non-empty string
        if row_id is None:
            raise ValueError(f"ID column '{id_column_name}' contains None value in row {i}")
        
        if not isinstance(row_id, str):
            raise ValueError(
                f"ID column '{id_column_name}' must contain strings. "
                f"Found {type(row_id).__name__} in row {i}: {repr(row_id)}. "
                f"Please convert your ID column to string dtype before running inference."
            )
        
        if row_id.strip() == "":
            raise ValueError(f"ID column '{id_column_name}' contains empty string in row {i}")
        
        if api_type == "completion":
            # For completion API, data should be a string
            if not isinstance(data, str):
                raise ValueError(
                    f"For api_type='completion', input data must be strings. "
                    f"Found {type(data).__name__} in row {i}: {data}"
                )
        
        elif api_type == "chat-completion":
            # For chat-completion API, use OpenAI's pydantic models for validation
            if not isinstance(data, list):
                raise ValueError(
                    f"For api_type='chat-completion', input data must be a list of messages. "
                    f"Found {type(data).__name__} in row {i}: {data}"
                )
            
            if len(data) == 0:
                raise ValueError(f"Empty message list found in row {i}")
            
            # Validate each message using OpenAI's pydantic models
            message_adapter = TypeAdapter(list[ChatCompletionMessageParam])
            
            try:
                # This will validate the entire messages list according to OpenAI's schema
                message_adapter.validate_python(data)
            except ValidationError as e:
                raise ValueError(
                    f"Invalid message format in row {i}. Messages must conform to OpenAI's ChatCompletionMessageParam format. "
                    f"Common issues: missing 'role' or 'content' fields, invalid role values, or incorrect data types.\n"
                    f"Validation error: {str(e)}\n"
                    f"Message data: {data}"
                ) from e
        
        elif api_type == "classification":
            # For classification API, data should be a string
            if not isinstance(data, str):
                raise ValueError(
                    f"For api_type='classification', input data must be strings. "
                    f"Found {type(data).__name__} in row {i}: {data}"
                )

        else:
            raise ValueError(f"Invalid API type: {api_type}")
    
    logger.info(f"Input data format validation passed for api_type='{api_type}' with string ID column '{id_column_name}' using OpenAI's pydantic models")


def validate_dataset_from_config(config_path: str, shard: int = None, num_shards: int = None):
    """
    Validate dataset format based on config file.
    
    Args:
        config_path: Path to the YAML configuration file
        shard: Optional shard number for validation (if None, validates full dataset)
        num_shards: Total number of shards (required if shard is specified)
    """
    logger.info(f"Loading configuration from: {config_path}")
    config = load_config_for_validation(config_path)
    
    logger.info("Loading dataset for validation...")
    if config['use_load_from_disk']:
        logger.info("Loading dataset with load_from_disk")
        ds = hfds.load_from_disk(config['dataset_path'])
    else:
        logger.info(f"Loading dataset with load_dataset with kwargs: {config['load_dataset_kwargs']}")
        kwargs = config['load_dataset_kwargs']
        ds = hfds.load_dataset(str(config['dataset_path']), **kwargs)

    # Apply sharding if specified
    if shard is not None and num_shards is not None:
        logger.info(f"Applying shard {shard} of {num_shards} for validation")
        ds = ds.shard(num_shards=num_shards, index=shard)
    
    logger.info(f"Dataset loaded: {len(ds)} rows")
    
    # Validate the dataset format
    logger.info("Starting data validation...")
    validate_input_data_format(
        ds, 
        config['input_column_name'], 
        config['id_column_name'], 
        config['api_type']
    )
    
    logger.info("✓ Data validation completed successfully!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Validate dataset format for LLM inference")
    parser.add_argument(
        "--config", 
        type=str, 
        required=True, 
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--shard", 
        type=int, 
        default=None,
        help="Shard number to validate (optional, validates full dataset if not specified)"
    )
    parser.add_argument(
        "--num-shards", 
        type=int, 
        default=None,
        help="Total number of shards (required if --shard is specified)"
    )
    
    args = parser.parse_args()
    
    # Validate shard parameters
    if args.shard is not None and args.num_shards is None:
        logger.error("--num-shards must be specified when --shard is provided")
        sys.exit(1)
    
    if args.shard is not None and args.num_shards is not None:
        if args.shard >= args.num_shards or args.shard < 0:
            logger.error(f"shard ({args.shard}) must be between 0 and {args.num_shards - 1}")
            sys.exit(1)
    
    try:
        validate_dataset_from_config(args.config, args.shard, args.num_shards)
        logger.info("Data validation passed! Dataset is ready for inference.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 