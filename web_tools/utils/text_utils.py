import re
from bs4 import BeautifulSoup


def clean_file_content(content):
    """
    Cleans the file content by removing HTML tags, extra whitespace, and special characters
    that might interfere with the OpenAI API.

    :param content: The raw file content as a string
    :return: The cleaned content as a string
    """
    # Remove HTML tags using BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text()

    # Replace curly braces with safe equivalents or remove them
    text = text.replace("{", "{{").replace("}", "}}")

    # Remove other special characters if needed
    # Here we replace anything that's not a word character (a-z, A-Z, 0-9) or common punctuation with a space
    # text = re.sub(r"[^\w\s.,!?'-]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_markdown_content(content):
    # def clean_html_blocks(content):
    """
    Cleans the HTML blocks within a Markdown content, preserving the Markdown structure.

    :param content: The raw Markdown content as a string
    :return: The content with cleaned HTML blocks as a string
    """

    def clean_html(html):
        # Use BeautifulSoup to remove HTML tags
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()

    # Pattern to identify HTML blocks
    html_block_pattern = re.compile(r"(<[^>]+>.*?</[^>]+>)", re.DOTALL)

    # Split the content by HTML blocks
    segments = html_block_pattern.split(content)

    cleaned_segments = []
    for segment in segments:
        if html_block_pattern.match(segment):
            # Clean the HTML block
            cleaned_segment = clean_html(segment)
            cleaned_segments.append(cleaned_segment)
        else:
            # Keep Markdown content intact
            cleaned_segments.append(segment)

    # Join the cleaned segments back into a single string
    cleaned_content = "".join(cleaned_segments)
    cleaned_content = cleaned_content.replace("{", "{{").replace("}", "}}")
    return cleaned_content
