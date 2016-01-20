class HTMLFormatter(object):
    """
        Formatter object for creating HTML Documents
    """
    import copy
    
    def __init__(self):
        pass

    def write(self, element):
        """
            Format data into html tag given a dictionary describing the
                html element

            Parameters
            ----------
                element : dict
                    Dictionary describing html element with 
                    tag, attrib, and text keys

            Returns
            -------
                html_string : str
                    string representation of html element
                    (eg "<p id='p1'>This is a paragraph</p>")

            TODO
            ----
                1 : Manage copy.copy usage.  Is it needed at all?
        """
        return _write_element(element)
    
    def _dict_handler(self, element, attrib_name=None):
        """
            TODO
            ----
                1 : attrib_name == 'href' little funky--think about decorator
                        or command pattern
        """
        if isinstance(element, dict):
            element = self.copy.copy(element)

            element_strings = {key: ','.join(value) 
                               if type(value)==list else value 
                               for key, value in element.iteritems()}

            if attrib_name == 'href':
            
                markers = {'cc': '?',
                           'bcc': '?',
                           'subject': '&'}


                element_format_string = \
                    ''.join(['mailto:{email}'] + 
                        [markers.get(key, '&') + '{0}={{{0}}}'.format(key)
                            for key in sorted(element_strings.keys())
                            if key != 'email']
                    )

            if attrib_name == 'style':
                element_format_string = \
                    ''.join(['{0}:{{{0}}};'.format(key)
                            for key in sorted(element_strings.keys())
                            if key != 'email']
                    )

            else:
                element_format_string = '&'.join(['{0}={{{0}}}'.format(key)
                            for key in sorted(element_strings.keys())])


            element = element_format_string.format(**element_strings)
            element = element.replace(' ', '%20')
        return element

    def _attrib_handler(self, attrib):
        self.copy.copy(attrib)
        for key in attrib:
            attrib[key] = self._dict_handler(attrib[key], key)
        attrib_string = ' '.join(['='.join([key, "'" + str(value) + "'"]) 
                                  for key, value in sorted(attrib.items(), key=lambda x: x[0])])
        return attrib_string

    def _make_element(self, element):
        element = self.copy.copy(element)
        if 'attrib' in element:
            element['attrib'] = self._attrib_handler(element['attrib'])
        return element

    
    def _validate_element(self, element):
        element = copy.copy(element)
        defaults = {'tag': 'div', 'attrib': '', 'text': ''}
        for key in defaults:
            element[key] = element.get(key, defaults[key])
        return element
    
    def _format_string(self, element):
        html_string = '<{tag} {attrib}>{text}</{tag}>'.format(**element)
        return html_string

    def _write_element(self, element):
        
        element = self._make_element(element)
        html_string = self._format_string(element)
        return html_string
    
    
class Element(HTMLFormatter):

    def __init__(self, tag='', attrib={}, text=''):
        
        self.tag = tag

        for key in attrib:
            attrib[key] = self._dict_handler(attrib[key], key)
            setattr(self, key, attrib[key])

        self.attrib = self._attrib_handler(attrib)
        self.text = text
        self.element = {'tag': self.tag, 
                        'attrib': self.attrib, 
                        'text': self.text }

        self.children = []
    
    def __getitem__(self, i):
        return self.children[i]
    
    def build_html(self):
        return ''.join(self._make_stack())
               
    def add(self, child_element):
        if not isinstance(child_element, self.__class__):
            raise ValueError("""children must be {0} datatype
                                {1} is {2}""".format(self.__class__, 
                                                     child_element, 
                                                     type(child_element)))

        self.children.append(child_element)
        return self
            
    def _make_stack(self, stack=None, indent=0):
        if stack==None:stack=[]
        opening_tag = "<{0} {1}>".format(self.tag, self.attrib)
        if self.text != '':
            opening_tag += "{0}".format(self.text)
        stack.append(opening_tag)

        for child in self.children:
            child._make_stack(stack, indent+1)
        end_tag = "</{0}>".format(self.tag)
        stack.append(end_tag)
        return stack


class EmptyElement(Element):
    def _make_stack(self, stack=None, indent=0):
        if stack==None:stack=[]
        stack.append('<{0}>'.format(self.tag))
        return stack


class HTMLStyle(object):
    
    
    def __init__(self, elements):
        self.body = Element('div', {'id': 'HTMLStyle_Container'}, '')
        for e in elements:
            setattr(self, 'add_{0}'.format(e), self._add_element(e))
        
    def _add_element(self, e):
        
        def func(text='', attrib={}):
            element = eval('self._build_{0}'.format(e))(text, attrib)
            self.body.add(element)
        
        return func
    
    def build_html(self):
        return self.body.build_html()
        
        



