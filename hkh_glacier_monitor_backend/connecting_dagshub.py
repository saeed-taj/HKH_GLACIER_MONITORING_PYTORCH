from dagshub.repo_bucket import get_repo_bucket_client

# boto3 client
boto_client = get_repo_bucket_client("saeed-taj/glacier_inference_cache")

# s3fs client
s3fs_client = get_repo_bucket_client("saeed-taj/glacier_inference_cache", flavor="s3fs")


def get_cache_key(glacier_name: str, year: int):
    return f"{glacier_name}/{year}/optical.tif"

def load_from_cache(glacier_name : str, year : int , local_path: str) -> bool:
    try:
        boto_client.download_file(
            Bucket="glacier_inference_cache",
            key=get_cache_key(glacier_name , year),
            Filename = local_path,
        )

        return True

    except Exception:
        return False


def save_to_cache(local_path : str, glacier_name: str, year: int ):
    boto_client.upload_file(
        Filename= local_path,
        Bucket="glacier_inference_cache",
        key=get_cache_key(glacier_name, year),
    )
    