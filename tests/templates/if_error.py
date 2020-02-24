def get_html(kwargs):
    template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error</title>
</head>
<body>

'''
    if kwargs['var'] == 1:
        template += '''        <p>1</p>
'''
    else:
        template += '''        <p>2</p>
'''
    elif kwargs['var'] == 2:
        template += '''        <p>3</p>
'''
    template += '''

</body>
</html>'''
    return template
