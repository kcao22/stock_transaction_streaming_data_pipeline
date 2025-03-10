import boto3
import os

from airflow.models import Variable


def _choose_s3_bucket(is_test: bool, bucket: str):
    if is_test:
        match bucket.lower():
            case "s3_ingress":
                return "ingress"
            case "s3_archive":
                return "archive"


def _create_client():
    client = boto3.client(
        "s3",
        aws_access_key_id=Variable.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=Variable.get("AWS_SECRET_ACCESS_KEY"),
    )
    return client


def put_object(is_test: bool, bucket: str, key: str, body: str, **kwargs) -> None:
    """
    Puts object to target s3 bucket. If local, writes to a mimic bucket in /opt/airflow/files/.
    @param is_test: If True, then local. Else AWS prod environment.
    @param bucket: If local, the folder of interest. Else S3 target bucket name.
    @param key: Full prefix and name of file.
    @param body: Content of file.
    @param kwargs: Keyword arguments.
    @return: File key.
    """
    if is_test:
        try:
            if key.startswith("/"):
                key = key[1:]
            file_path = os.path.join("/opt/airflow/files/", key)
            print(f"Key: {key}")
            if not os.path.exists(file_path):
                os.makedirs(name=os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(body)
        except Exception as e:
            raise Exception(f"Failed to put object to target bucket {bucket} with object path {key}. Exception: {e}")
    else:
        try:
            client = _create_client()
            client.put_object(
                Bucket=_choose_s3_bucket(is_test=is_test, bucket=bucket),
                Key=key,
                Body=body,
                **kwargs
            )
        except Exception as e:
            raise Exception(f"Failed to put object for {key} to bucket {bucket} with exception: {e}") from e


def get_object(is_test: bool, bucket: str, key: str, **kwargs) -> dict:
    """
    Gets object from a bucket.
    @param is_test: If True, then local. Else AWS prod environment.
    @param bucket: Bucket name.
    @param key: Full path of the object.
    @param kwargs: Keyword arguments.
    @return: Object content.
    """
    if is_test:
        try:
            with open(f"/opt/airflow/files/{_choose_s3_bucket(is_test=is_test, bucket=bucket)}/{key}", "rb") as f:
                return {"Body": f.read()}
        except UnicodeDecodeError:
            with open(f"/opt/airflow/files/{_choose_s3_bucket(is_test=is_test, bucket=bucket)}/{key}", "rb") as f:
                return {"Body": f.read()}
    else:
        client = _create_client()
        return client.put_object(
            Bucket=_choose_s3_bucket(is_test=is_test, bucket=bucket),
            Key=key,
            **kwargs
        )


def copy_object(is_test: bool, source_bucket: str, source_key: str, target_bucket: str, target_key: str, **kwargs) -> None:
    """
    Copies object from a source bucket to target bucket.
    @param is_test: If True, then local. Else AWS prod environment.
    @param source_bucket: Source bucket name.
    @param source_key: Full path of the source object.
    @param target_bucket: Target bucket name.
    @param target_key: Full path of target object.
    @param kwargs: Keyword arguments.
    @return: None.
    """
    if is_test:
        body = get_object(
            is_test=is_test, 
            bucket=_choose_s3_bucket(is_test=is_test, bucket=source_bucket), 
            key=source_key
        )["Body"]
        put_object(
            is_test=is_test, 
            bucket=_choose_s3_bucket(is_test=is_test, bucket=target_bucket), 
            key=target_key, 
            body=body
        )
    else:
        try:
            client = _create_client()
            client.copy_object(
                Bucket=_choose_s3_bucket(is_test=is_test, bucket=target_bucket),
                Key=target_key,
                CopySource={"Bucket": source_bucket, "Key": source_key},
            )
        except Exception as e:
            raise Exception(f"Failed to copy object from source bucket {source_bucket} with object path {source_key} to target bucket {target_bucket} with object path {target_key}. Exception: {e}") from e


def delete_object(is_test: bool, bucket: str, key: str, **kwargs) -> None:
    if is_test:
        os.remove(f"/opt/airflow/files/{key}")
    else:
        client = _create_client()
        client.delete_object(
            Bucket=_choose_s3_bucket(is_test=is_test, bucket=bucket),
            Key=key,
            **kwargs
        )
