def make_ipython_notebook(issue, target_location=None):
    """Make a new IPython notebook based on JIRA ticket

    Parameters
    ----------
        issue : str
            JIRA ticket number

    Returns
    -------
        None

    Example
    -------
        make_ipython_notebook('REL-3021')
    """
    from .apiclients import IpynbClient, JiraHTMLMediator
    from .writers import HTMLWriter_01

    ipc = IpynbClient()

    if not target_location:
        target_location = issue
    try:
        j = JiraHTMLMediator(issue, HTMLWriter_01)
        html_string = j.build_html()
        ipc.write(html_string, 'markdown')
    except Exception as e:
        print '{}:'.format(repr(e))
        print '  JIRA was ignored'
        ipc.write('<h2>{0}</h2>'.format(issue, 'markdown'))

    basic_imports = [
        "import pandas as pd\n",
        "import numpy as np\n",
        "import matplotlib.pyplot as plt\n",
        "import relpy as rp\n",
        "import turntable as tt\n",
        "\n",
        "pd.set_option('display.max_columns', 500)\n",
        "pd.set_option('display.max_row', 100)\n",
        "\n",
        "%matplotlib inline\n",
        "%autosave 60"
       ]
    ipc.write(''.join(basic_imports), 'code')
    ipc.write('', 'code')
    ipc.write('<h3>Save Files</h3>', 'markdown')
    ipc.write("%%export", 'code')
    ipc.save(target_location)
