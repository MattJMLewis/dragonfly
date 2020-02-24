def get_html(kwargs):
    template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error</title>
</head>
<body>

'''
    for item in kwargs['items']:
        template += '''        ''' + str(kwargs['item']) + '''
'''
    template += '''

</body>
</html>'''
    return template
