import base64

from typing import Union, Tuple

from urllib.parse import urlparse
from github import Github


def parse_github_url(url: str) -> Tuple[str, str]:
    """
    Parses the GitHub repository name and file path from a given URL.

    :param url: The GitHub URL to parse
    :return: A tuple containing the repository name and file path
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")

    # The repository name is in the format 'owner/repo'
    repo_name = "/".join(path_parts[:2])

    # The file path starts after 'blob/branch'
    file_path = "/".join(path_parts[4:])

    return repo_name, file_path


def read_file_from_github(token, repo_name, file_path) -> Union[str, None]:
    """
    Reads the content of a file from a GitHub repository.

    :param token: GitHub personal access token
    :param repo_name: Name of the repository in the format 'owner/repo'
    :param file_path: Path to the file within the repository
    :return: Contents of the file as a string
    """
    # Initialize Github object using the access token
    g = Github(token)

    try:
        # Get the repository object
        repo = g.get_repo(repo_name)

        # Get the file contents
        file_content = repo.get_contents(file_path)

        # Decode the file content from base64
        content = base64.b64decode(file_content.content).decode("utf-8")

        return content

    except Exception as e:
        return str(e)


# # Example usage
# if __name__ == "__main__":
#     # Replace with your GitHub personal access token
#     token = os.getenv("GITHUB_ACCESS_TOKEN")
#     repo_name, file_name = parse_github_url("https://github.com/assafelovic/gpt-researcher/blob/master/README.md")
#     # Replace with the repository name in 'owner/repo' format
#     #file_content = read_file_from_github(token, "assafelovic/gpt-researcher", "README.md")
#     file_content = read_file_from_github(token, repo_name, file_name)
#     cleaned_file_content = clean_markdown_content(file_content)

#     # print(file_content)
#     print(cleaned_file_content)
