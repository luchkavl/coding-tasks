from typing import List

from tags import non_content_tags, word_tags, tags_to_process


def get_open_tag_indexes(html: str) -> List[int]:
    open_index = html.find('<')
    close_index = html[open_index:].find('>') + open_index
    return [open_index, close_index]


def get_close_tag_indexes(html: str, tag_name: str, open_tag_indexes: List[int], last_close_tag_indexes=None) -> List[int]:
    # first open tag close bracket's index in orig link
    open_tag_close_index = open_tag_indexes[1]

    open_index = None
    close_index = None
    # first close tag - indexes
    if not last_close_tag_indexes:
        open_index = html[open_tag_close_index:].find(f'</{tag_name}') + open_tag_close_index
        close_index = html[open_index:].find('>') + open_index
    else:
        last_close_tag_cl_br_idx = last_close_tag_indexes[1]
        open_index = html[last_close_tag_cl_br_idx:].find(f'</{tag_name}') + last_close_tag_cl_br_idx
        close_index = html[open_index:].find('>') + open_index

    # content between first open tag and first found close tag
    content_between_cl_and_o = html[open_tag_close_index + 1:open_index]

    # check is same tag exist between first open tag and first found close tag
    same_index_exist = content_between_cl_and_o.find(f'<{tag_name}')

    # if same tag exist found his open and close brackets indexes
    if same_index_exist != -1:
        # tag indexes in content_between_cl_and_o
        same_tag_1_open_br_idx = same_index_exist
        same_tag_1_close_br_idx = content_between_cl_and_o[same_tag_1_open_br_idx:].find('>') + same_tag_1_open_br_idx

        # tag indexes in orig html
        same_tag_1_open_br_idx += open_tag_close_index + 1
        same_tag_1_close_br_idx += open_tag_close_index + 1

        same_open_tag_indexes = [same_tag_1_open_br_idx, same_tag_1_close_br_idx]

        last_close_tag_indexes = [open_index, close_index]
        result_to_return = get_close_tag_indexes(
            html,
            tag_name,
            same_open_tag_indexes,
            last_close_tag_indexes=last_close_tag_indexes)
        return result_to_return
    else:
        return [open_index, close_index]


def get_tag_name(html, tag_indexes: List[int]) -> str:
    tag_name = ''
    open_index = tag_indexes[0]
    close_index = tag_indexes[1]
    for char in html[open_index + 1:close_index + 1]:
        if char != ' ' and char != '>':
            tag_name += char
        else:
            break
    return tag_name.lower()


def get_last_printable_char(content, open_tag_indexes: List[int]):
    text_in_open_tag = content[open_tag_indexes[0] + 1:open_tag_indexes[1]]
    for char in text_in_open_tag[::-1]:
        if char.isprintable():
            return char


def get_content(html, open_tag_close: int, close_tag_open: int) -> dict:
    content = html[open_tag_close + 1:close_tag_open]
    if content.find('<') != -1:
        return html_to_dict(content)
    else:
        return content


def get_text_wo_word_tags(content, open_tag_indexes: List[int], close_tag_indexes: List[int]) -> str:
    text_before_o_tag = content[:open_tag_indexes[0]]
    text_between_tags = content[open_tag_indexes[1] + 1: close_tag_indexes[0]]
    text_after_cl_tag = content[close_tag_indexes[1] + 1:]

    result = text_before_o_tag + text_between_tags + text_after_cl_tag
    return result


def save_content_to_dict(tag_name, tag_dict, content):
    tag_name_in_dict = tag_name in tag_dict

    if not tag_name_in_dict:
        tag_dict[tag_name] = content
    else:
        new_name_for_dict = None
        counter = 0
        while tag_name_in_dict:
            counter += 1
            new_name_for_dict = f'{tag_name}_{counter}'
            tag_name_in_dict = new_name_for_dict in tag_dict

        tag_dict[new_name_for_dict] = content


def html_to_dict(html):
    html = ' '.join(html.split())
    html_dict = {}

    tags_still_exist = 1
    content_to_parse = html
    while tags_still_exist != -1 and content_to_parse != ' ' and content_to_parse != '':
        if content_to_parse.find('<') != -1:
            stripped_content_for_text_bef_tag = content_to_parse.strip()
            first_tag_in_content_idx = stripped_content_for_text_bef_tag.find('<')
            if first_tag_in_content_idx > 0:
                content_before_tag = stripped_content_for_text_bef_tag[:first_tag_in_content_idx].strip()

                save_content_to_dict(tag_name='text_in_tag', tag_dict=html_dict, content=content_before_tag)

        open_tag_indexes = get_open_tag_indexes(content_to_parse)
        tag_name = get_tag_name(content_to_parse, open_tag_indexes)

        # info for check is it self-closing tag or not.
        open_tag_last_char = get_last_printable_char(content_to_parse, open_tag_indexes)

        if tag_name in tags_to_process and tag_name not in non_content_tags:
            close_tag_indexes = get_close_tag_indexes(content_to_parse, tag_name, open_tag_indexes)
            if tag_name not in word_tags:
                content = get_content(content_to_parse, open_tag_indexes[1], close_tag_indexes[0])

                if content != '' and len(content) != 0:
                    if isinstance(content, str):
                        stripped_content = content.strip()
                        save_content_to_dict(tag_name, html_dict, stripped_content)
                    else:
                        save_content_to_dict(tag_name, html_dict, content)

                content_to_parse = content_to_parse[close_tag_indexes[1] + 1:]
                if content_to_parse.strip() != '':
                    if content_to_parse.find('<') == -1:
                        content_to_save = content_to_parse.strip()
                        save_content_to_dict(tag_name='text_in_tag', tag_dict=html_dict, content=content_to_save)
                        tags_still_exist = content_to_parse.find('<')
                    else:
                        tags_still_exist = content_to_parse.find('<')
                else:
                    tags_still_exist = content_to_parse.find('<')

            else:
                content_to_parse = get_text_wo_word_tags(content_to_parse, open_tag_indexes, close_tag_indexes)
                tags_still_exist = content_to_parse.find('<')
                if tags_still_exist == -1:
                    return content_to_parse
        elif open_tag_last_char == '/' or tag_name.startswith('!'):
            content_to_parse = content_to_parse[open_tag_indexes[1] + 1:]
        else:
            close_tag_indexes = get_close_tag_indexes(content_to_parse, tag_name, open_tag_indexes)
            content_to_parse = content_to_parse[close_tag_indexes[1] + 1:]

    return html_dict


def values_from_dict_generator(html_dict):
    for value in html_dict.values():
        if isinstance(value, dict):
            yield from values_from_dict_generator(value)
        else:
            yield value


def convert_html_to_text(html: str):
    html_dict = html_to_dict(html)
    contents_list = list(values_from_dict_generator(html_dict))
    if len(contents_list) != 0:
        if len(contents_list) == 1 and contents_list[0] == '':
            return 'There is no text content in html'
        else:
            return '\n' + '\n'.join(contents_list) + '\n'
    else:
        return 'There is no text content in html'


# 1 test
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
assert convert_html_to_text(html) == expected_text, "html to text conversion failed"

# 2 test
html = """
<h1>Hello this is my Super WebApp</h1>
"""

expected_text = """
Hello this is my Super WebApp
"""
assert convert_html_to_text(html) == expected_text, "html to text conversion failed"

# 3 test
html = """
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head><title>My Supper App</title></head>
<body>
<a
   >
text</a
>
</body>
</html>
"""

expected_text = """
text
"""
assert convert_html_to_text(html) == expected_text, "html to text conversion failed"

# 4 test
html = """
<h1>Hello this is my Super WebApp </h1><h2>    Hello this is my Super WebApp  </h2>
"""

expected_text = """
Hello this is my Super WebApp
Hello this is my Super WebApp
"""
assert convert_html_to_text(html) == expected_text, "html to text conversion failed"

# 5 test
html = """
<div class="main">
  <h1 class="document-title">
    <a href="../javascript-examples.html" class="breadcrumb breadcrumbWithArrow">JAVASCRIPT EXAMPLES</a>
    Complex Table Sort
    <div class="pageActionsShell">
      <div id="page-actions" class="pageActions"><a href="source-code/table-sort-complex.html" class="buttonLink">SOURCE</a></div>
    </div>
  </h1>
</div>
"""

expected_text = """
JAVASCRIPT EXAMPLES
Complex Table Sort
SOURCE
"""
assert convert_html_to_text(html) == expected_text, "html to text conversion failed"

# 6 test
html = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Complex Table Sort | JavaScript Examples | UIZE JavaScript Framework</title>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
  <meta name="keywords" content="Uize.Widget.TableSort"/>
  <meta name="description" content="See an example of a sortable data table, where one column has complex HTML and some rows are fixed. No problem - the table sort widget handles it all!"/>
  <link rel="alternate" type="application/rss+xml" title="UIZE JavaScript Framework - Latest News" href="http://www.uize.com/latest-news.rss"/>
  <link rel="stylesheet" href="../css/page.css"/>
  <link rel="stylesheet" href="../css/page.example.css"/>
  <link rel="stylesheet" href="../css/widget.datatable.css"/>
  <style type="text/css">
    table.fruitName td {
      font-size:11px;
      font-weight:bold;
      border:1px solid #ccc;
      padding:0 4px;
      background:#ccc;
      text-align:center;
    }
  </style>
</head>
<body>
Hello
</body>
</html>
"""

expected_text = """
Hello
"""
assert convert_html_to_text(html) == expected_text, "html to text conversion failed"

# 7 test
html = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Complex Table Sort | JavaScript Examples | UIZE JavaScript Framework</title>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
  <meta name="keywords" content="Uize.Widget.TableSort"/>
  <meta name="description" content="See an example of a sortable data table, where one column has complex HTML and some rows are fixed. No problem - the table sort widget handles it all!"/>
  <link rel="alternate" type="application/rss+xml" title="UIZE JavaScript Framework - Latest News" href="http://www.uize.com/latest-news.rss"/>
  <link rel="stylesheet" href="../css/page.css"/>
  <link rel="stylesheet" href="../css/page.example.css"/>
  <link rel="stylesheet" href="../css/widget.datatable.css"/>
  <style type="text/css">
    table.fruitName td {
      font-size:11px;
      font-weight:bold;
      border:1px solid #ccc;
      padding:0 4px;
      background:#ccc;
      text-align:center;
    }
  </style>
</head>
<body>
<a>

</a>
</body>
</html>
"""

expected_text = 'There is no text content in html'

assert convert_html_to_text(html) == expected_text, "html to text conversion failed"