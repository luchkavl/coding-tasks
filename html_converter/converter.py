import re

# tags
tags = {
    "html",
    "head",
    "meta",
    "link",
    "body",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "strong",
    "b",
    "i",
    "u",
    "p",
    "script",
    "style",
    "div",
    "span",
    "iframe",
    "pre",
    "a",
    "ul",
    "ol",
    "li",
    "table",
    "tbody",
    "tr",
    "td",
}


def convert_html_to_text(html: str) -> str:
    # write code here
    body_indexes_pattern = re.compile(r"<body>(.*)</body>", re.DOTALL)
    body_indexes = re.search(body_indexes_pattern, html).span()
    body = html[body_indexes[0]:body_indexes[1]]

    body_wo_indent = '\n'.join([line.lstrip() for line in body.split('\n')])

    for tag in tags:
        a = r'<' + tag + '>'
        b = '</' + tag + '>'

        body_wo_indent = body_wo_indent.replace(a, '')
        body_wo_indent = body_wo_indent.replace(b, '')

    for tag in tags:
        open_closed_tag_pattern = re.compile(rf"<{tag} ", re.DOTALL)
        open_closed_tag_search = re.search(open_closed_tag_pattern, body_wo_indent)

        while open_closed_tag_search:
            open_closed_tag_indexes = open_closed_tag_search.span()
            open_tag = open_closed_tag_indexes[0]
            close_index = body_wo_indent[open_tag:].find('>')
            tag_to_delete = body_wo_indent[open_tag:open_tag + close_index + 1]

            body_wo_indent = body_wo_indent.replace(tag_to_delete, '')

            open_closed_tag_search = re.search(open_closed_tag_pattern, body_wo_indent)

    return '\n' + '\n'.join([line for line in body_wo_indent.split('\n') if line != '']) + '\n'


html = """
<html>
    <head>
        <meta name="application-name" content="Super WebApp">
        <link rel="home" href="/home">
        <style data-href="https://whatever.com/some_link</style>
        <script nonce="">onStyleLoad();</script>
    </head>
    <body>
        <h1>Hello this is my Super WebApp</h1>
        <div>
            <span class="paragraph bold">First line <u>from</u> first paragraph</span>
        </div>
        <pre id="pre_id_main" class="some_class">
            <span class="funny underline">First line from <b>second</b> paragraph</span>
        </pre>
    </body>
</html>
"""

expected_text = """
Hello this is my Super WebApp
First line from first paragraph
First line from second paragraph
"""

convert_html_to_text(html)

assert convert_html_to_text(html) == expected_text, "html to text conversion failed"