from src.parsing.date_parser import parse_article_datetime

HTML = """
<html><head>
<meta property="article:published_time" content="2025-10-18T09:30:00+07:00"/>
</head><body><article>Test</article></body></html>
"""

def test_meta_datetime():
    dt, s = parse_article_datetime(HTML, "https://example.com/2025/10/18/test.htm", {
        "date_selectors": ["meta[property='article:published_time']::content"],
        "url_date_regex": None,
    })
    assert dt is not None
    assert s.endswith(":30")
