from .formatters import Element, EmptyElement, HTMLStyle

class HTMLWriter_01(HTMLStyle):
    """
    Class for formatting jira ticket information in HTML
    """

    def __init__(self):
        key = '_build_'
        nKey = len(key)
        __elements__ = [e[nKey:] for e in dir(self) if e[:nKey] == key]
        super(self.__class__, self).__init__(__elements__)

        
    def _build_header(self, (name, link_url, summary), attrib):
        if link_url==None:link_url='#'+name
        span = Element('span', {}, '')
        div = Element('div', {'id': '_'.join(name.split()), 
                              'style': 'display:inline-block; float:left;'})
        font = Element('font', {'size': '5em'}, name)
        a = self._build_link('', {'href': link_url})
        b = Element('b')
        
        a.add(font)
        div.add(a)
        b.add(div)
        
        
        if summary:
            div_s = Element('div', {'id': 'Summary'})
            font_s = Element('font', {'size': '4em'}, '&mdash;' + summary)
            a_s = self._build_anchor(summary)
            
            div_s.add(font_s)
            div_s.add(a_s)
            b.add(div_s)
            
        span.add(b)
        return span
        
    def _build_tab(self, attrib={}, text=''):
        return Element('span', {}, '&nbsp;' * 4)
        
    def _build_date(self, date_string, attrib={}):
        text = 'Prepared on: {0}'.format(date_string)
        return Element('code', attrib, text)
    
    def _build_title(self, name, attrib={}):
        return Element('h3', attrib, name)
    
    def _build_text(self, text, attrib={}):
        return Element('p', attrib, text)
    
    def _build_link(self, display, attrib={}):
        
        attrib['style'] = attrib.get('style', {})
        attrib['style']['color'] = attrib['style'].get('color', {})
        attrib['style']['color'] = '#CC0000'
        attrib['style']['font-weight'] = attrib['style'].get('font-weight', {})
        attrib['style']['font-weight'] = 'bold'
        
        return Element('a', attrib, display)
    
    def _build_anchor(self, name, attrib={}):
        return self._build_link('&#182;', {'class': 'anchor-link', 'href': '#{0}'.format(name)})
    
    def _build_code(self, text, attrib={}):
        return Element('code', attrib, text)
    
    def _build_contact(self, (title, name), attrib={}):
        link = self._build_link(name, attrib)
        contact = self._build_code('{0}: '.format(title), {})
        contact.add(link)
        return contact
    
    def _build_attachment(self, file_name, attrib={}):
        link = self._build_link('', {'href': file_name, 'target': '_blank'})
        display_name = self._build_code(file_name, attrib)

        link.add(display_name)
        
        return link

    def _build_break(self, text='', attrib={}):
        br = EmptyElement('br')
        return br
        
        
        