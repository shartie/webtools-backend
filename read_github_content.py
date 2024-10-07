
import re
import base64
import os

from typing import Union    

from urllib.parse import urlparse

from github import Github
from bs4 import BeautifulSoup

from web_tools.utils.github_utils import parse_github_url, read_file_from_github
from web_tools.utils.text_utils import clean_markdown_content

# Example usage
if __name__ == "__main__":
    # Replace with your GitHub personal access token
    token = os.getenv("GITHUB_ACCESS_TOKEN")
    repo_name, file_name = parse_github_url("https://github.com/assafelovic/gpt-researcher/blob/master/README.md")
    # Replace with the repository name in 'owner/repo' format
    #file_content = read_file_from_github(token, "assafelovic/gpt-researcher", "README.md")
    file_content = read_file_from_github(token, repo_name, file_name)
    cleaned_file_content = clean_markdown_content(file_content)

    # print(file_content)
    print(cleaned_file_content)
