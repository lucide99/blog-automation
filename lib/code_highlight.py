"""Pygments 기반 인라인 CSS 코드 하이라이팅"""

import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter


FORMATTER = HtmlFormatter(
    noclasses=True,  # 인라인 CSS (외부 스타일시트 불필요)
    style="monokai",
    linenos=False,
    cssclass="code-block",
)


def highlight_code_blocks(html: str) -> str:
    """HTML 내 <pre><code> 블록을 Pygments로 하이라이팅"""

    def replace_block(match):
        lang = match.group(1) or ""
        code = match.group(2)
        # HTML 엔티티 복원
        code = (code
            .replace("&quot;", '"')
            .replace("&#x27;", "'")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
        )

        try:
            if lang:
                lexer = get_lexer_by_name(lang, stripall=True)
            else:
                lexer = guess_lexer(code)
        except Exception:
            return match.group(0)

        return highlight(code, lexer, FORMATTER)

    # markdown 라이브러리가 생성하는 형식: <pre><code class="language-python">...</code></pre>
    pattern = r'<pre><code class="language-(\w+)">(.*?)</code></pre>'
    html = re.sub(pattern, replace_block, html, flags=re.DOTALL)

    # class 없는 코드 블록도 처리
    pattern_no_lang = r'<pre><code>(.*?)</code></pre>'
    html = re.sub(pattern_no_lang, lambda m: replace_block(type('', (), {'group': lambda self, i: {0: m.group(0), 1: '', 2: m.group(1)}[i]})()), html, flags=re.DOTALL)

    return html
