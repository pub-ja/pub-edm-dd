import re

with open(r'c:\PART_DRIVE\project\ke-mail-form\pub-edm-dd\edm-feedback-report-test.html', encoding='utf-8') as f:
    content = f.read()

# 1. outer table
content = content.replace(
    '<table width="790" cellpadding="0" cellspacing="0" border="0"\n\tstyle="table-layout:fixed; min-width: 790px; width:790px; border-collapse:collapse; border: 1px solid #e7eaf0; background:#fff; font-family:-apple-system, \'Apple SD Gothic Neo\', sans-serif;">',
    '<table cellpadding="0" cellspacing="0" border="0" align="center"\n\tstyle="width:100%; max-width:790px; border-collapse:collapse; border: 1px solid #e7eaf0; background:#fff; font-family:-apple-system, \'Apple SD Gothic Neo\', sans-serif;">'
)

# 2. 파란 줄 colspan
content = content.replace(
    '<td colspan="3" style="height:4px; background-color:#051766; font-size:0; line-height:0;">',
    '<td style="height:4px; background-color:#051766; font-size:0; line-height:0;">'
)

# 3. colspan="3" spacer rows (height만 있는 단순 row)
content = re.sub(
    r'<tr><td colspan="3" (height="\d+" style="height:\d+px; font-size:0; line-height:0;")</s*></td></tr>',
    r'<tr><td \1></td></tr>',
    content
)
# 위 패턴이 안 잡히는 경우 직접 처리
content = re.sub(
    r'<tr><td colspan="3" height="(\d+)" style="(height:\d+px; font-size:0; line-height:0;)"></td></tr>',
    r'<tr><td height="\1" style="\2"></td></tr>',
    content
)

# 4. 통계요약 background row
content = content.replace(
    '<tr style="background-color:#F5FBFE;"><td colspan="3" height="20" style="height:20px; font-size:0; line-height:0;"></td></tr>',
    '<tr style="background-color:#F5FBFE;"><td height="20" style="height:20px; font-size:0; line-height:0;"></td></tr>'
)
content = content.replace(
    '<tr style="background-color:#F5FBFE;"><td colspan="3" height="16" style="height:16px; font-size:0; line-height:0;"></td></tr>',
    '<tr style="background-color:#F5FBFE;"><td height="16" style="height:16px; font-size:0; line-height:0;"></td></tr>'
)

# 5. 3-column rows with 45px spacers → single td with padding
# 패턴: <tr[\s\S]*?>\n\t\t<td width="45"...></td>\n\t\t<td ...>CONTENT</td>\n\t\t<td width="45"...></td>\n\t</tr>
def replace_45_rows(html):
    pattern = re.compile(
        r'(\t<tr(?:[^>]*)>)\n'
        r'\t\t<td width="45" style="width:45px;"></td>\n'
        r'(\t\t<td(?:(?!\n\t\t<td).)*?</td>)\n'
        r'\t\t<td width="45" style="width:45px;"></td>\n'
        r'\t</tr>',
        re.DOTALL
    )
    def repl(m):
        tr_tag = m.group(1)
        inner = m.group(2).strip()
        # inner td에 padding:0 45px 추가
        # style= 앞에 padding 삽입
        inner = re.sub(r'^(\t\t<td)((?:\s+(?:width|height)="[^"]*")*)\s+style="', r'\1\2 style="padding:0 45px; ', inner)
        if 'padding:0 45px' not in inner:
            inner = re.sub(r'^(\t\t<td)', r'\1 style="padding:0 45px;"', inner)
        return tr_tag + '\n' + inner + '\n\t</tr>'
    return pattern.sub(repl, html)

content = replace_45_rows(content)

# 6. 헤더 로고 행 (별도 처리 - width="700" height="84px" 있는 케이스)
content = content.replace(
    '\t<tr>\n\t\t<td width="45" style="width:45px;"></td>\n\t\t<td width="700" style="width:700px; height:84px;">\n\t\t\t<img src="https://raw.githubusercontent.com/pub-ja/pub-edm-dd/main/images/img--edm-header-logo.jpg" alt="KOREAN AIR"\n\t\t\t\tstyle="display:block; width:200px; height:auto; border:0;">\n\t\t</td>\n\t\t<td width="45" style="width:45px;"></td>\n\t</tr>',
    '\t<tr>\n\t\t<td style="padding:0 45px; height:84px;">\n\t\t\t<img src="https://raw.githubusercontent.com/pub-ja/pub-edm-dd/main/images/img--edm-header-logo.jpg" alt="KOREAN AIR"\n\t\t\t\tstyle="display:block; width:200px; height:auto; border:0;">\n\t\t</td>\n\t</tr>'
)

# 7. 통계요약 카드 행 (45px + 700px table + 45px)
content = content.replace(
    '\t<tr style="background-color:#F5FBFE;">\n\t\t<td width="45" style="width:45px;"></td>\n\t\t<td>\n\t\t\t<!-- 통계 요약 : 4개 개별 카드 -->\n\t\t\t<table width="700" cellpadding="0" cellspacing="0" border="0"\n\t\t\t\tstyle="table-layout:fixed; width:700px; border-collapse:collapse;">',
    '\t<tr style="background-color:#F5FBFE;">\n\t\t<td style="padding:0 45px;">\n\t\t\t<!-- 통계 요약 : 4개 개별 카드 -->\n\t\t\t<table width="700" cellpadding="0" cellspacing="0" border="0"\n\t\t\t\tstyle="table-layout:fixed; width:700px; border-collapse:collapse;">'
)
content = content.replace(
    '\t\t</td>\n\t\t<td width="45" style="width:45px;"></td>\n\t</tr>\n\t<tr style="background-color:#F5FBFE;"><td height="20"',
    '\t\t</td>\n\t</tr>\n\t<tr style="background-color:#F5FBFE;"><td height="20"'
)

# 8. 카드 outer wrapper row (45px + div+table700 + 45px)
# 이 패턴들은 다양해서 남은 45px spacer를 일괄 제거
# 남은 <td width="45" style="width:45px;"></td> 가 있는 tr 처리
def cleanup_remaining_45(html):
    # <tr>\n\t\t<td width="45"...></td>\n ... content (multiline) ... \n\t\t<td width="45"...></td>\n\t</tr>
    pattern = re.compile(
        r'(\t<tr(?:[^>]*)>)\n'
        r'\t\t<td width="45" style="width:45px;"></td>\n'
        r'((?:(?!\t\t<td width="45").)*?)'
        r'\t\t<td width="45" style="width:45px;"></td>\n'
        r'\t</tr>',
        re.DOTALL
    )
    def repl(m):
        tr_tag = m.group(1)
        inner = m.group(2)
        # inner의 첫 번째 td에 padding 추가
        inner = re.sub(
            r'^(\t\t<td)((?:\s+\w+="[^"]*")*)\s+style="',
            r'\1\2 style="padding:0 45px; ',
            inner,
            count=1
        )
        if 'padding:0 45px' not in inner:
            inner = re.sub(r'^(\t\t<td)(?!\s+style)', r'\1 style="padding:0 45px;"', inner, count=1)
        return tr_tag + '\n' + inner + '\t</tr>'
    prev = None
    while prev != html:
        prev = html
        html = pattern.sub(repl, html)
    return html

content = cleanup_remaining_45(content)

# 9. 카드 내부 table (700px) → width:100%
content = re.sub(
    r'<table width="700" cellpadding="0" cellspacing="0" border="0"\s*\n\s*style="table-layout:fixed; width:700px; border-collapse:collapse; background:#fff;">',
    '<table width="100%" cellpadding="0" cellspacing="0" border="0"\n\t\t\t\tstyle="width:100%; border-collapse:collapse; background:#fff;">',
    content
)
# 들여쓰기 다른 버전
content = re.sub(
    r'<table width="700" cellpadding="0" cellspacing="0" border="0"\s*\n\s*style="table-layout:fixed; width:700px; border-collapse:collapse; background:#fff;">',
    '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; border-collapse:collapse; background:#fff;">',
    content
)

# 10. 카드 내부 29px spacer rows 제거 → padding으로
# 상하 spacer: <td width="29"...> <td height=...> <td width="29"...>
content = re.sub(
    r'<td width="29" style="width:29px;"></td>\n(\s*)<td (height="\d+" style="height:\d+px; font-size:0; line-height:0;")></td>\n\s*<td width="29" style="width:29px;"></td>',
    r'<td \2></td>',
    content
)

# 코멘트 텍스트 td: 29px + content td + 29px
content = re.sub(
    r'<td width="29" style="width:29px;"></td>\n(\s*)<td (style="font-size:14px[^"]*")>',
    r'<td \2 padding:0 29px;">',
    content
)
# 더 정확하게
content = re.sub(
    r'<td width="29" style="width:29px;"></td>\n(\t+)<td style="font-size:14px; color:#051766; line-height:1\.6; text-align:left;">',
    r'<td style="padding:0 29px; font-size:14px; color:#051766; line-height:1.6; text-align:left;">',
    content
)

# 코멘트 텍스트 닫힘 후 29px
content = re.sub(
    r'(<!-- \{comment_text\} -->\n\t+</td>)\n\t+<td width="29" style="width:29px;"></td>',
    r'\1',
    content
)

# 배지/버튼 wrapper td: 29px + <td>\n<table width="642"...> + 29px
content = re.sub(
    r'<td width="29" style="width:29px;"></td>\n(\t+)<td>\n(\t+)<table width="642" cellpadding="0" cellspacing="0" border="0" style="table-layout:fixed; width:642px;">',
    r'<td style="padding:0 29px;">\n\2<table width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; border-collapse:collapse;">',
    content
)

# 배지/버튼 table 닫힘 후 29px
content = re.sub(
    r'(</table>\n\t+</td>)\n\t+<td width="29" style="width:29px;"></td>(\n\t+</tr>\n\t+<tr>\n\t+<td width="29" style="width:29px;"></td>\n\t+<td height="24")',
    r'\1\2',
    content
)

# 남은 29px spacer 정리
content = re.sub(r'\n\t+<td width="29" style="width:29px;"></td>\n(\t+<td height="\d+")', r'\n\1', content)
content = re.sub(r'(<td height="\d+" style="height:\d+px; font-size:0; line-height:0;"></td>)\n\t+<td width="29" style="width:29px;"></td>', r'\1', content)

with open(r'c:\PART_DRIVE\project\ke-mail-form\pub-edm-dd\edm-feedback-report-v2.html', 'w', encoding='utf-8') as f:
    f.write(content)

# 남은 45px, 29px spacer 개수 확인
remaining_45 = content.count('<td width="45" style="width:45px;">')
remaining_29 = content.count('<td width="29" style="width:29px;">')
print(f'남은 45px spacer: {remaining_45}')
print(f'남은 29px spacer: {remaining_29}')
print('Done')
