#   Copyright 2009 Thilo Fromm
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from xml.parsers import expat
import sys


# TODO: JSON implementation

"""
RestMS resource description processor.
    The processor will parse incoming XML or JSON and run callbacks upon
    certain events.

 p = create_processor( content_type )
    Simple factory which returns a processor instance soutable to parse 
    the _content_type_ provided. Content type may be "restms+xml" or 
    "restms+json". 
    "None" is returned if the content type is unknown to the parser.

 p.init( element_attribute_callbacks )
    Initialize the parser instance.
    _element_attribute_callbacks_ is a dictionary of dictionaries 
    containing callbacks for all attributes of each element.

    The callbacks dictionary is structured like this:
    { "element A name" : { ELEMENT_START        : callback,
                           "attribute_1_name"   : callback,
                           "attribute_2_name"   : callback},
      "element B name" : { ELEMENT_START        : callback,
                           "attribute_1_name"   : callback,
                           "attribute_2_name"   : callback,
                           CONTENT_DATA         : callback},
      ...
    }

    The special attribute value ELEMENT_START is required and determines
    a callback to be run for the element itself, i.e. before all the 
    attribute callbacks are executed. Specifying an attribute value of 
    CONTENT_DATA will run the corresponding callback when content data 
    is encountered while processing an element. 

    callback signature
    ------------------
        for attributes:
    def callback(attribute, value)
        for ELEMENT_START:
    def callback(element, parent)
        for CONTENT_DATA:
    def callback(element, content)

    Callbacks take two arguments. The first argument is always set to the 
    element encountered. 
    Attribute callbacks will get the value of the corresponding attribute 
    (i.e. when encountering brim="foo", the "brim" callback will be run with 
    value "foo"). 
    ELEMENT_START callbacks will be run with the name of the parent element
    (i.e. with "<message> <header /> </message>" input the "header" handler 
    will be called with the parent set to "message" ).  If "element" is a 
    top level element the value will be an empty string, i.e. "".
    CONTENT_DATA callbacks will receive the content data in the second
    argument.

    example
    -------

    This, for example, will define a dictionary for parsing a "message" resource:
    { "message" : { "address"    : lambda value: msgdata.address    = value,
                    "message_id" : lambda value: msgdata.message_id = value,
                    "reply_to"   : lambda value: msgdata.reply_to   = value}
      "header"  : { ELEMENT_START: lambda value: self._add_header(msg, val),
                    "name"       : ....,
                  }
    }

 p.process( data, final )
    Main function which processes unicode strings in _data_.
    Tha parser must be initialized in advance by calling p.init().
    Can be called repeatedly. _final_ must be true when calling
    the function for the last time.

    exceptions
    ----------

    The parser will throw an exception if an unspecified element or attribute
    is encountered. Furthermore an exception is thrown upon encounter of an
    element for which no ELEMENT_START callback was defined.
 
    If content is encountered within an elmennt and no CONTENT_DATA callback
    was provided, the data will be silently ignored (this eases parsing as
    every space between elements counts as data).

"""


ELEMENT_START= 1
CONTENT_DATA = 2

class RestMSProcessor(object):
    """Abstract base class for RestMS processor classes"""

    def init  (self, callbacks):
        """Callbacks initialization function to be implemented 
            by concrete classes"""
        raise AttributeError("Abstract")

    def process(self, input_data):
        """Main processor function to be implemented by concrete classes"""
        raise AttributeError("Abstract")


class RestMSProcessorException(Exception):
    """ This exception is thrown when the parser encounters an irregularity
        in the input or fails internally. Exception payload is a descriptive
        text of what was encountered. Use case example:
        ----
        try: p.process()
        except RestMSProcessorException, e: return HttpResponseBadRequest(e.message)
        ------
        """



class RestMSXMLProcessor(RestMSProcessor):
    """ Simple RestMS XML parser.
        The parser uses the expat non-validating XML parser to manipulate 
        RestMS resource properties."""

    #  ---  Parser helper functions ---

    def _in_restms_xml(self, key):
        """Returns true if we are within <restms> XML; updates the 
           internal state when we are about to enter restms xml.
           """
        ret = self._rest_xml
        if key == "restms": 
            if self._rest_xml: 
                _exc(HttpResponseBadRequest, 
                        "parser error: <restms> tag within <restms> tag")
            self._rest_xml = True
        return ret


    #  ---  ExPat callback functions ---

    def _start_elem(self, element, attributes):
        """XML parser start element callback.
           The method checks the incoming element and its attributes 
           and calls user-defined attribute handlers."""
        if not self._in_restms_xml(element): return

        # run the "start element" callback
        try:
            if self._elements: 
                parent = self._elements[-1]
                self._elements_cb[element][ELEMENT_START](element,parent)
            else:
                self._elements_cb[element][ELEMENT_START](element, "")
        except KeyError:
            raise RestMSProcessorException(
                "Unsupported element %s" % element )

        self._elements.append( element )

        # now run the attribute callbacks
        try:
            for a in attributes:
                self._elements_cb[element][a](a, attributes[a])
        except KeyError:
            raise RestMSProcessorException(
                "Unsupported attribute %s in element %s" % 
                (a, element) )

    def _data(self, data):
        """Data XML parser callback"""
        if not self._elements:
           return
        element = self._elements[-1]
        if CONTENT_DATA in self._elements_cb[element]:
            self._elements_cb[element][CONTENT_DATA](element, data)


    def _end_elem(self, element):
        """End element XML parser callback """
        if not self._elements:
           return
        self._elements.pop()

    #
    #  ---  public access functions  ---
    #

    def init(self, callbacks): 
        """XML Parser initialisation"""
        self._rest_xml = False
        self._elements_cb = callbacks
        self._elements = []

        self._xp = expat.ParserCreate()
        self._xp.returns_unicode = True
        self._xp.buffer_text = True
        self._xp.specified_attributes = True

        self._xp.StartElementHandler = self._start_elem
        self._xp.EndElementHandler = self._end_elem
        self._xp.CharacterDataHandler = self._data

    def process(self, data, final):
        try:
            self._xp.Parse(data, final)
        except expat.ExpatError, e:
            raise RestMSProcessorException(
                "XML Parser error in line %s, char %s" % (e.lineno, e.offset) )

