# This file was generated from MyFormatterGrammar.peg
# See https://canopy.jcoglan.com/ for documentation

from collections import defaultdict
import re


class TreeNode(object):
    def __init__(self, text, offset, elements):
        self.text = text
        self.offset = offset
        self.elements = elements

    def __iter__(self):
        for el in self.elements:
            yield el


class TreeNode1(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode1, self).__init__(text, offset, elements)
        self.variable = elements[0]
        self.conversion = elements[1]


class TreeNode2(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode2, self).__init__(text, offset, elements)
        self.value_conversion = elements[0]


class TreeNode3(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode3, self).__init__(text, offset, elements)
        self.negation = elements[0]
        self.variable = elements[1]
        self.conversion = elements[2]
        self.true_value = elements[3]
        self.false_value = elements[4]


class TreeNode4(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode4, self).__init__(text, offset, elements)
        self.condition_conversion = elements[0]


class TreeNode5(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode5, self).__init__(text, offset, elements)
        self.everything = elements[0]


class TreeNode6(TreeNode):
    def __init__(self, text, offset, elements):
        super(TreeNode6, self).__init__(text, offset, elements)
        self.everything = elements[0]


FAILURE = object()


class Grammar(object):
    REGEX_1 = re.compile('^[ \\t\\n\\r]')
    REGEX_2 = re.compile('^[^%]')
    REGEX_3 = re.compile('^[\\[\\]\\|]')
    REGEX_4 = re.compile('^[a-zA-Z0-9_]')
    REGEX_5 = re.compile('^[jJ]')
    REGEX_6 = re.compile('^[^\\WjJ]')
    REGEX_7 = re.compile('^[jJ]')
    REGEX_8 = re.compile('^[lL]')
    REGEX_9 = re.compile('^[^\\WlLuU]')
    REGEX_10 = re.compile('^[lLuU]')
    REGEX_11 = re.compile('^[uU]')
    REGEX_12 = re.compile('^[^\\WlLuU]')
    REGEX_13 = re.compile('^[lLuU]')
    REGEX_14 = re.compile('^[rR]')
    REGEX_15 = re.compile('^[^\\WrR]')
    REGEX_16 = re.compile('^[rR]')

    def _read_everything(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['everything'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0, address1 = self._offset, [], None
        while True:
            index2 = self._offset
            address1 = self._read_text()
            if address1 is FAILURE:
                self._offset = index2
                address1 = self._read_value()
                if address1 is FAILURE:
                    self._offset = index2
                    address1 = self._read_condition()
                    if address1 is FAILURE:
                        self._offset = index2
            if address1 is not FAILURE:
                elements0.append(address1)
            else:
                break
        if len(elements0) >= 0:
            address0 = TreeNode(self._input[index1:self._offset], index1, elements0)
            self._offset = self._offset
        else:
            address0 = FAILURE
        if address0 is not FAILURE:
            cls0 = type(address0)
            address0.__class__ = type(cls0.__name__ + 'Everything', (cls0, self._types.Everything), {})
        self._cache['everything'][index0] = (address0, self._offset)
        return address0

    def _read__(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['_'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        chunk0, max0 = None, self._offset + 1
        if max0 <= self._input_size:
            chunk0 = self._input[self._offset:max0]
        if chunk0 is not None and Grammar.REGEX_1.search(chunk0):
            address0 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
            self._offset = self._offset + 1
        else:
            address0 = FAILURE
            if self._offset > self._failure:
                self._failure = self._offset
                self._expected = []
            if self._offset == self._failure:
                self._expected.append(('Formatting::_', '[ \\t\\n\\r]'))
        self._cache['_'][index0] = (address0, self._offset)
        return address0

    def _read_text(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['formatter'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0, address1 = self._offset, [], None
        while True:
            index2 = self._offset
            chunk0, max0 = None, self._offset + 1
            if max0 <= self._input_size:
                chunk0 = self._input[self._offset:max0]
            if chunk0 is not None and Grammar.REGEX_2.search(chunk0):
                address1 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                self._offset = self._offset + 1
            else:
                address1 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append(('Formatting::formatter', '[^%]'))
            if address1 is FAILURE:
                self._offset = index2
                address1 = self._read_escape()
                if address1 is FAILURE:
                    self._offset = index2
                    index3, elements1 = self._offset, []
                    address2 = FAILURE
                    chunk1, max1 = None, self._offset + 1
                    if max1 <= self._input_size:
                        chunk1 = self._input[self._offset:max1]
                    if chunk1 == '%':
                        address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                        self._offset = self._offset + 1
                    else:
                        address2 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append(('Formatting::formatter', '"%"'))
                    if address2 is not FAILURE:
                        elements1.append(address2)
                        address3 = FAILURE
                        index4 = self._offset
                        chunk2, max2 = None, self._offset + 1
                        if max2 <= self._input_size:
                            chunk2 = self._input[self._offset:max2]
                        if chunk2 is not None and Grammar.REGEX_3.search(chunk2):
                            address3 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                            self._offset = self._offset + 1
                        else:
                            address3 = FAILURE
                            if self._offset > self._failure:
                                self._failure = self._offset
                                self._expected = []
                            if self._offset == self._failure:
                                self._expected.append(('Formatting::formatter', '[\\[\\]\\|]'))
                        self._offset = index4
                        if address3 is FAILURE:
                            address3 = TreeNode(self._input[self._offset:self._offset], self._offset, [])
                            self._offset = self._offset
                        else:
                            address3 = FAILURE
                        if address3 is not FAILURE:
                            elements1.append(address3)
                        else:
                            elements1 = None
                            self._offset = index3
                    else:
                        elements1 = None
                        self._offset = index3
                    if elements1 is None:
                        address1 = FAILURE
                    else:
                        address1 = TreeNode(self._input[index3:self._offset], index3, elements1)
                        self._offset = self._offset
                    if address1 is FAILURE:
                        self._offset = index2
            if address1 is not FAILURE:
                elements0.append(address1)
            else:
                break
        if len(elements0) >= 1:
            address0 = self._actions.text(self._input, index1, self._offset, elements0)
            self._offset = self._offset
        else:
            address0 = FAILURE
        self._cache['formatter'][index0] = (address0, self._offset)
        return address0

    def _read_escape(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['escape'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        chunk0, max0 = None, self._offset + 2
        if max0 <= self._input_size:
            chunk0 = self._input[self._offset:max0]
        if chunk0 == '%%':
            address0 = self._actions.escape(self._input, self._offset, self._offset + 2, [])
            self._offset = self._offset + 2
        else:
            address0 = FAILURE
            if self._offset > self._failure:
                self._failure = self._offset
                self._expected = []
            if self._offset == self._failure:
                self._expected.append(('Formatting::escape', '"%%"'))
        self._cache['escape'][index0] = (address0, self._offset)
        return address0

    def _read_variable(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['variable'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0, address1 = self._offset, [], None
        while True:
            chunk0, max0 = None, self._offset + 1
            if max0 <= self._input_size:
                chunk0 = self._input[self._offset:max0]
            if chunk0 is not None and Grammar.REGEX_4.search(chunk0):
                address1 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                self._offset = self._offset + 1
            else:
                address1 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append(('Formatting::variable', '[a-zA-Z0-9_]'))
            if address1 is not FAILURE:
                elements0.append(address1)
            else:
                break
        if len(elements0) >= 1:
            address0 = TreeNode(self._input[index1:self._offset], index1, elements0)
            self._offset = self._offset
        else:
            address0 = FAILURE
        self._cache['variable'][index0] = (address0, self._offset)
        return address0

    def _read_value(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['value'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        chunk0, max0 = None, self._offset + 2
        if max0 <= self._input_size:
            chunk0 = self._input[self._offset:max0]
        if chunk0 == '%[':
            address1 = TreeNode(self._input[self._offset:self._offset + 2], self._offset, [])
            self._offset = self._offset + 2
        else:
            address1 = FAILURE
            if self._offset > self._failure:
                self._failure = self._offset
                self._expected = []
            if self._offset == self._failure:
                self._expected.append(('Formatting::value', '"%["'))
        if address1 is not FAILURE:
            address2 = FAILURE
            address2 = self._read_variable()
            if address2 is not FAILURE:
                elements0.append(address2)
                address3 = FAILURE
                index2 = self._offset
                index3, elements1 = self._offset, []
                address4 = FAILURE
                chunk1, max1 = None, self._offset + 1
                if max1 <= self._input_size:
                    chunk1 = self._input[self._offset:max1]
                if chunk1 == '!':
                    address4 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                    self._offset = self._offset + 1
                else:
                    address4 = FAILURE
                    if self._offset > self._failure:
                        self._failure = self._offset
                        self._expected = []
                    if self._offset == self._failure:
                        self._expected.append(('Formatting::value', '"!"'))
                if address4 is not FAILURE:
                    address5 = FAILURE
                    address5 = self._read_value_conversion()
                    if address5 is not FAILURE:
                        elements1.append(address5)
                    else:
                        elements1 = None
                        self._offset = index3
                else:
                    elements1 = None
                    self._offset = index3
                if elements1 is None:
                    address3 = FAILURE
                else:
                    address3 = TreeNode2(self._input[index3:self._offset], index3, elements1)
                    self._offset = self._offset
                if address3 is FAILURE:
                    address3 = TreeNode(self._input[index2:index2], index2, [])
                    self._offset = index2
                if address3 is not FAILURE:
                    elements0.append(address3)
                    address6 = FAILURE
                    chunk2, max2 = None, self._offset + 2
                    if max2 <= self._input_size:
                        chunk2 = self._input[self._offset:max2]
                    if chunk2 == ']%':
                        address6 = TreeNode(self._input[self._offset:self._offset + 2], self._offset, [])
                        self._offset = self._offset + 2
                    else:
                        address6 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append(('Formatting::value', '"]%"'))
                    if address6 is not FAILURE:
                        pass
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = TreeNode1(self._input[index1:self._offset], index1, elements0)
            self._offset = self._offset
        if address0 is not FAILURE:
            cls0 = type(address0)
            address0.__class__ = type(cls0.__name__ + 'Value', (cls0, self._types.Value), {})
        self._cache['value'][index0] = (address0, self._offset)
        return address0

    def _read_value_conversion(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['value_conversion'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0, address1 = self._offset, [], None
        while True:
            index2 = self._offset
            index3, elements1 = self._offset, []
            address2 = FAILURE
            chunk0, max0 = None, self._offset + 1
            if max0 <= self._input_size:
                chunk0 = self._input[self._offset:max0]
            if chunk0 is not None and Grammar.REGEX_5.search(chunk0):
                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                self._offset = self._offset + 1
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append(('Formatting::value_conversion', '[jJ]'))
            if address2 is not FAILURE:
                elements1.append(address2)
                address3 = FAILURE
                index4 = self._offset
                index5, elements2 = self._offset, []
                address4 = FAILURE
                index6, elements3, address5 = self._offset, [], None
                while True:
                    chunk1, max1 = None, self._offset + 1
                    if max1 <= self._input_size:
                        chunk1 = self._input[self._offset:max1]
                    if chunk1 is not None and Grammar.REGEX_6.search(chunk1):
                        address5 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                        self._offset = self._offset + 1
                    else:
                        address5 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append(('Formatting::value_conversion', '[^\\WjJ]'))
                    if address5 is not FAILURE:
                        elements3.append(address5)
                    else:
                        break
                if len(elements3) >= 0:
                    address4 = TreeNode(self._input[index6:self._offset], index6, elements3)
                    self._offset = self._offset
                else:
                    address4 = FAILURE
                if address4 is not FAILURE:
                    elements2.append(address4)
                    address6 = FAILURE
                    chunk2, max2 = None, self._offset + 1
                    if max2 <= self._input_size:
                        chunk2 = self._input[self._offset:max2]
                    if chunk2 is not None and Grammar.REGEX_7.search(chunk2):
                        address6 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                        self._offset = self._offset + 1
                    else:
                        address6 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append(('Formatting::value_conversion', '[jJ]'))
                    if address6 is not FAILURE:
                        elements2.append(address6)
                    else:
                        elements2 = None
                        self._offset = index5
                else:
                    elements2 = None
                    self._offset = index5
                if elements2 is None:
                    address3 = FAILURE
                else:
                    address3 = TreeNode(self._input[index5:self._offset], index5, elements2)
                    self._offset = self._offset
                self._offset = index4
                if address3 is FAILURE:
                    address3 = TreeNode(self._input[self._offset:self._offset], self._offset, [])
                    self._offset = self._offset
                else:
                    address3 = FAILURE
                if address3 is not FAILURE:
                    elements1.append(address3)
                else:
                    elements1 = None
                    self._offset = index3
            else:
                elements1 = None
                self._offset = index3
            if elements1 is None:
                address1 = FAILURE
            else:
                address1 = TreeNode(self._input[index3:self._offset], index3, elements1)
                self._offset = self._offset
            if address1 is FAILURE:
                self._offset = index2
                index7, elements4 = self._offset, []
                address7 = FAILURE
                chunk3, max3 = None, self._offset + 1
                if max3 <= self._input_size:
                    chunk3 = self._input[self._offset:max3]
                if chunk3 is not None and Grammar.REGEX_8.search(chunk3):
                    address7 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                    self._offset = self._offset + 1
                else:
                    address7 = FAILURE
                    if self._offset > self._failure:
                        self._failure = self._offset
                        self._expected = []
                    if self._offset == self._failure:
                        self._expected.append(('Formatting::value_conversion', '[lL]'))
                if address7 is not FAILURE:
                    elements4.append(address7)
                    address8 = FAILURE
                    index8 = self._offset
                    index9, elements5 = self._offset, []
                    address9 = FAILURE
                    index10, elements6, address10 = self._offset, [], None
                    while True:
                        chunk4, max4 = None, self._offset + 1
                        if max4 <= self._input_size:
                            chunk4 = self._input[self._offset:max4]
                        if chunk4 is not None and Grammar.REGEX_9.search(chunk4):
                            address10 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                            self._offset = self._offset + 1
                        else:
                            address10 = FAILURE
                            if self._offset > self._failure:
                                self._failure = self._offset
                                self._expected = []
                            if self._offset == self._failure:
                                self._expected.append(('Formatting::value_conversion', '[^\\WlLuU]'))
                        if address10 is not FAILURE:
                            elements6.append(address10)
                        else:
                            break
                    if len(elements6) >= 0:
                        address9 = TreeNode(self._input[index10:self._offset], index10, elements6)
                        self._offset = self._offset
                    else:
                        address9 = FAILURE
                    if address9 is not FAILURE:
                        elements5.append(address9)
                        address11 = FAILURE
                        chunk5, max5 = None, self._offset + 1
                        if max5 <= self._input_size:
                            chunk5 = self._input[self._offset:max5]
                        if chunk5 is not None and Grammar.REGEX_10.search(chunk5):
                            address11 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                            self._offset = self._offset + 1
                        else:
                            address11 = FAILURE
                            if self._offset > self._failure:
                                self._failure = self._offset
                                self._expected = []
                            if self._offset == self._failure:
                                self._expected.append(('Formatting::value_conversion', '[lLuU]'))
                        if address11 is not FAILURE:
                            elements5.append(address11)
                        else:
                            elements5 = None
                            self._offset = index9
                    else:
                        elements5 = None
                        self._offset = index9
                    if elements5 is None:
                        address8 = FAILURE
                    else:
                        address8 = TreeNode(self._input[index9:self._offset], index9, elements5)
                        self._offset = self._offset
                    self._offset = index8
                    if address8 is FAILURE:
                        address8 = TreeNode(self._input[self._offset:self._offset], self._offset, [])
                        self._offset = self._offset
                    else:
                        address8 = FAILURE
                    if address8 is not FAILURE:
                        elements4.append(address8)
                    else:
                        elements4 = None
                        self._offset = index7
                else:
                    elements4 = None
                    self._offset = index7
                if elements4 is None:
                    address1 = FAILURE
                else:
                    address1 = TreeNode(self._input[index7:self._offset], index7, elements4)
                    self._offset = self._offset
                if address1 is FAILURE:
                    self._offset = index2
                    index11, elements7 = self._offset, []
                    address12 = FAILURE
                    chunk6, max6 = None, self._offset + 1
                    if max6 <= self._input_size:
                        chunk6 = self._input[self._offset:max6]
                    if chunk6 is not None and Grammar.REGEX_11.search(chunk6):
                        address12 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                        self._offset = self._offset + 1
                    else:
                        address12 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append(('Formatting::value_conversion', '[uU]'))
                    if address12 is not FAILURE:
                        elements7.append(address12)
                        address13 = FAILURE
                        index12 = self._offset
                        index13, elements8 = self._offset, []
                        address14 = FAILURE
                        index14, elements9, address15 = self._offset, [], None
                        while True:
                            chunk7, max7 = None, self._offset + 1
                            if max7 <= self._input_size:
                                chunk7 = self._input[self._offset:max7]
                            if chunk7 is not None and Grammar.REGEX_12.search(chunk7):
                                address15 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                                self._offset = self._offset + 1
                            else:
                                address15 = FAILURE
                                if self._offset > self._failure:
                                    self._failure = self._offset
                                    self._expected = []
                                if self._offset == self._failure:
                                    self._expected.append(('Formatting::value_conversion', '[^\\WlLuU]'))
                            if address15 is not FAILURE:
                                elements9.append(address15)
                            else:
                                break
                        if len(elements9) >= 0:
                            address14 = TreeNode(self._input[index14:self._offset], index14, elements9)
                            self._offset = self._offset
                        else:
                            address14 = FAILURE
                        if address14 is not FAILURE:
                            elements8.append(address14)
                            address16 = FAILURE
                            chunk8, max8 = None, self._offset + 1
                            if max8 <= self._input_size:
                                chunk8 = self._input[self._offset:max8]
                            if chunk8 is not None and Grammar.REGEX_13.search(chunk8):
                                address16 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                                self._offset = self._offset + 1
                            else:
                                address16 = FAILURE
                                if self._offset > self._failure:
                                    self._failure = self._offset
                                    self._expected = []
                                if self._offset == self._failure:
                                    self._expected.append(('Formatting::value_conversion', '[lLuU]'))
                            if address16 is not FAILURE:
                                elements8.append(address16)
                            else:
                                elements8 = None
                                self._offset = index13
                        else:
                            elements8 = None
                            self._offset = index13
                        if elements8 is None:
                            address13 = FAILURE
                        else:
                            address13 = TreeNode(self._input[index13:self._offset], index13, elements8)
                            self._offset = self._offset
                        self._offset = index12
                        if address13 is FAILURE:
                            address13 = TreeNode(self._input[self._offset:self._offset], self._offset, [])
                            self._offset = self._offset
                        else:
                            address13 = FAILURE
                        if address13 is not FAILURE:
                            elements7.append(address13)
                        else:
                            elements7 = None
                            self._offset = index11
                    else:
                        elements7 = None
                        self._offset = index11
                    if elements7 is None:
                        address1 = FAILURE
                    else:
                        address1 = TreeNode(self._input[index11:self._offset], index11, elements7)
                        self._offset = self._offset
                    if address1 is FAILURE:
                        self._offset = index2
            if address1 is not FAILURE:
                elements0.append(address1)
            else:
                break
        if len(elements0) >= 0:
            address0 = TreeNode(self._input[index1:self._offset], index1, elements0)
            self._offset = self._offset
        else:
            address0 = FAILURE
        self._cache['value_conversion'][index0] = (address0, self._offset)
        return address0

    def _read_condition(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['condition'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0 = self._offset, []
        address1 = FAILURE
        chunk0, max0 = None, self._offset + 3
        if max0 <= self._input_size:
            chunk0 = self._input[self._offset:max0]
        if chunk0 == '%[%':
            address1 = TreeNode(self._input[self._offset:self._offset + 3], self._offset, [])
            self._offset = self._offset + 3
        else:
            address1 = FAILURE
            if self._offset > self._failure:
                self._failure = self._offset
                self._expected = []
            if self._offset == self._failure:
                self._expected.append(('Formatting::condition', '"%[%"'))
        if address1 is not FAILURE:
            address2 = FAILURE
            index2, elements1, address3 = self._offset, [], None
            while True:
                address3 = self._read__()
                if address3 is not FAILURE:
                    elements1.append(address3)
                else:
                    break
            if len(elements1) >= 0:
                address2 = TreeNode(self._input[index2:self._offset], index2, elements1)
                self._offset = self._offset
            else:
                address2 = FAILURE
            if address2 is not FAILURE:
                address4 = FAILURE
                index3 = self._offset
                chunk1, max1 = None, self._offset + 1
                if max1 <= self._input_size:
                    chunk1 = self._input[self._offset:max1]
                if chunk1 == '!':
                    address4 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                    self._offset = self._offset + 1
                else:
                    address4 = FAILURE
                    if self._offset > self._failure:
                        self._failure = self._offset
                        self._expected = []
                    if self._offset == self._failure:
                        self._expected.append(('Formatting::condition', '"!"'))
                if address4 is FAILURE:
                    address4 = TreeNode(self._input[index3:index3], index3, [])
                    self._offset = index3
                if address4 is not FAILURE:
                    elements0.append(address4)
                    address5 = FAILURE
                    address5 = self._read_variable()
                    if address5 is not FAILURE:
                        elements0.append(address5)
                        address6 = FAILURE
                        index4 = self._offset
                        index5, elements2 = self._offset, []
                        address7 = FAILURE
                        chunk2, max2 = None, self._offset + 1
                        if max2 <= self._input_size:
                            chunk2 = self._input[self._offset:max2]
                        if chunk2 == '!':
                            address7 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                            self._offset = self._offset + 1
                        else:
                            address7 = FAILURE
                            if self._offset > self._failure:
                                self._failure = self._offset
                                self._expected = []
                            if self._offset == self._failure:
                                self._expected.append(('Formatting::condition', '"!"'))
                        if address7 is not FAILURE:
                            address8 = FAILURE
                            address8 = self._read_condition_conversion()
                            if address8 is not FAILURE:
                                elements2.append(address8)
                            else:
                                elements2 = None
                                self._offset = index5
                        else:
                            elements2 = None
                            self._offset = index5
                        if elements2 is None:
                            address6 = FAILURE
                        else:
                            address6 = TreeNode4(self._input[index5:self._offset], index5, elements2)
                            self._offset = self._offset
                        if address6 is FAILURE:
                            address6 = TreeNode(self._input[index4:index4], index4, [])
                            self._offset = index4
                        if address6 is not FAILURE:
                            elements0.append(address6)
                            address9 = FAILURE
                            index6, elements3, address10 = self._offset, [], None
                            while True:
                                address10 = self._read__()
                                if address10 is not FAILURE:
                                    elements3.append(address10)
                                else:
                                    break
                            if len(elements3) >= 0:
                                address9 = TreeNode(self._input[index6:self._offset], index6, elements3)
                                self._offset = self._offset
                            else:
                                address9 = FAILURE
                            if address9 is not FAILURE:
                                address11 = FAILURE
                                index7 = self._offset
                                index8, elements4 = self._offset, []
                                address12 = FAILURE
                                chunk3, max3 = None, self._offset + 3
                                if max3 <= self._input_size:
                                    chunk3 = self._input[self._offset:max3]
                                if chunk3 == '%|%':
                                    address12 = TreeNode(self._input[self._offset:self._offset + 3], self._offset, [])
                                    self._offset = self._offset + 3
                                else:
                                    address12 = FAILURE
                                    if self._offset > self._failure:
                                        self._failure = self._offset
                                        self._expected = []
                                    if self._offset == self._failure:
                                        self._expected.append(('Formatting::condition', '"%|%"'))
                                if address12 is not FAILURE:
                                    address13 = FAILURE
                                    address13 = self._read_everything()
                                    if address13 is not FAILURE:
                                        elements4.append(address13)
                                    else:
                                        elements4 = None
                                        self._offset = index8
                                else:
                                    elements4 = None
                                    self._offset = index8
                                if elements4 is None:
                                    address11 = FAILURE
                                else:
                                    address11 = TreeNode5(self._input[index8:self._offset], index8, elements4)
                                    self._offset = self._offset
                                if address11 is FAILURE:
                                    address11 = TreeNode(self._input[index7:index7], index7, [])
                                    self._offset = index7
                                if address11 is not FAILURE:
                                    elements0.append(address11)
                                    address14 = FAILURE
                                    index9 = self._offset
                                    index10, elements5 = self._offset, []
                                    address15 = FAILURE
                                    chunk4, max4 = None, self._offset + 3
                                    if max4 <= self._input_size:
                                        chunk4 = self._input[self._offset:max4]
                                    if chunk4 == '%|%':
                                        address15 = TreeNode(self._input[self._offset:self._offset + 3], self._offset, [])
                                        self._offset = self._offset + 3
                                    else:
                                        address15 = FAILURE
                                        if self._offset > self._failure:
                                            self._failure = self._offset
                                            self._expected = []
                                        if self._offset == self._failure:
                                            self._expected.append(('Formatting::condition', '"%|%"'))
                                    if address15 is not FAILURE:
                                        address16 = FAILURE
                                        address16 = self._read_everything()
                                        if address16 is not FAILURE:
                                            elements5.append(address16)
                                        else:
                                            elements5 = None
                                            self._offset = index10
                                    else:
                                        elements5 = None
                                        self._offset = index10
                                    if elements5 is None:
                                        address14 = FAILURE
                                    else:
                                        address14 = TreeNode6(self._input[index10:self._offset], index10, elements5)
                                        self._offset = self._offset
                                    if address14 is FAILURE:
                                        address14 = TreeNode(self._input[index9:index9], index9, [])
                                        self._offset = index9
                                    if address14 is not FAILURE:
                                        elements0.append(address14)
                                        address17 = FAILURE
                                        chunk5, max5 = None, self._offset + 3
                                        if max5 <= self._input_size:
                                            chunk5 = self._input[self._offset:max5]
                                        if chunk5 == '%]%':
                                            address17 = TreeNode(self._input[self._offset:self._offset + 3], self._offset, [])
                                            self._offset = self._offset + 3
                                        else:
                                            address17 = FAILURE
                                            if self._offset > self._failure:
                                                self._failure = self._offset
                                                self._expected = []
                                            if self._offset == self._failure:
                                                self._expected.append(('Formatting::condition', '"%]%"'))
                                        if address17 is not FAILURE:
                                            pass
                                        else:
                                            elements0 = None
                                            self._offset = index1
                                    else:
                                        elements0 = None
                                        self._offset = index1
                                else:
                                    elements0 = None
                                    self._offset = index1
                            else:
                                elements0 = None
                                self._offset = index1
                        else:
                            elements0 = None
                            self._offset = index1
                    else:
                        elements0 = None
                        self._offset = index1
                else:
                    elements0 = None
                    self._offset = index1
            else:
                elements0 = None
                self._offset = index1
        else:
            elements0 = None
            self._offset = index1
        if elements0 is None:
            address0 = FAILURE
        else:
            address0 = TreeNode3(self._input[index1:self._offset], index1, elements0)
            self._offset = self._offset
        if address0 is not FAILURE:
            cls0 = type(address0)
            address0.__class__ = type(cls0.__name__ + 'Condition', (cls0, self._types.Condition), {})
        self._cache['condition'][index0] = (address0, self._offset)
        return address0

    def _read_condition_conversion(self):
        address0, index0 = FAILURE, self._offset
        cached = self._cache['condition_conversion'].get(index0)
        if cached:
            self._offset = cached[1]
            return cached[0]
        index1, elements0, address1 = self._offset, [], None
        while True:
            index2, elements1 = self._offset, []
            address2 = FAILURE
            chunk0, max0 = None, self._offset + 1
            if max0 <= self._input_size:
                chunk0 = self._input[self._offset:max0]
            if chunk0 is not None and Grammar.REGEX_14.search(chunk0):
                address2 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                self._offset = self._offset + 1
            else:
                address2 = FAILURE
                if self._offset > self._failure:
                    self._failure = self._offset
                    self._expected = []
                if self._offset == self._failure:
                    self._expected.append(('Formatting::condition_conversion', '[rR]'))
            if address2 is not FAILURE:
                elements1.append(address2)
                address3 = FAILURE
                index3 = self._offset
                index4, elements2 = self._offset, []
                address4 = FAILURE
                index5, elements3, address5 = self._offset, [], None
                while True:
                    chunk1, max1 = None, self._offset + 1
                    if max1 <= self._input_size:
                        chunk1 = self._input[self._offset:max1]
                    if chunk1 is not None and Grammar.REGEX_15.search(chunk1):
                        address5 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                        self._offset = self._offset + 1
                    else:
                        address5 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append(('Formatting::condition_conversion', '[^\\WrR]'))
                    if address5 is not FAILURE:
                        elements3.append(address5)
                    else:
                        break
                if len(elements3) >= 0:
                    address4 = TreeNode(self._input[index5:self._offset], index5, elements3)
                    self._offset = self._offset
                else:
                    address4 = FAILURE
                if address4 is not FAILURE:
                    elements2.append(address4)
                    address6 = FAILURE
                    chunk2, max2 = None, self._offset + 1
                    if max2 <= self._input_size:
                        chunk2 = self._input[self._offset:max2]
                    if chunk2 is not None and Grammar.REGEX_16.search(chunk2):
                        address6 = TreeNode(self._input[self._offset:self._offset + 1], self._offset, [])
                        self._offset = self._offset + 1
                    else:
                        address6 = FAILURE
                        if self._offset > self._failure:
                            self._failure = self._offset
                            self._expected = []
                        if self._offset == self._failure:
                            self._expected.append(('Formatting::condition_conversion', '[rR]'))
                    if address6 is not FAILURE:
                        elements2.append(address6)
                    else:
                        elements2 = None
                        self._offset = index4
                else:
                    elements2 = None
                    self._offset = index4
                if elements2 is None:
                    address3 = FAILURE
                else:
                    address3 = TreeNode(self._input[index4:self._offset], index4, elements2)
                    self._offset = self._offset
                self._offset = index3
                if address3 is FAILURE:
                    address3 = TreeNode(self._input[self._offset:self._offset], self._offset, [])
                    self._offset = self._offset
                else:
                    address3 = FAILURE
                if address3 is not FAILURE:
                    elements1.append(address3)
                else:
                    elements1 = None
                    self._offset = index2
            else:
                elements1 = None
                self._offset = index2
            if elements1 is None:
                address1 = FAILURE
            else:
                address1 = TreeNode(self._input[index2:self._offset], index2, elements1)
                self._offset = self._offset
            if address1 is not FAILURE:
                elements0.append(address1)
            else:
                break
        if len(elements0) >= 0:
            address0 = TreeNode(self._input[index1:self._offset], index1, elements0)
            self._offset = self._offset
        else:
            address0 = FAILURE
        self._cache['condition_conversion'][index0] = (address0, self._offset)
        return address0


class Parser(Grammar):
    def __init__(self, input, actions, types):
        self._input = input
        self._input_size = len(input)
        self._actions = actions
        self._types = types
        self._offset = 0
        self._cache = defaultdict(dict)
        self._failure = 0
        self._expected = []

    def parse(self):
        tree = self._read_everything()
        if tree is not FAILURE and self._offset == self._input_size:
            return tree
        if not self._expected:
            self._failure = self._offset
            self._expected.append(('Formatting', '<EOF>'))
        raise ParseError(format_error(self._input, self._failure, self._expected))


class ParseError(SyntaxError):
    pass


def parse(input, actions=None, types=None):
    parser = Parser(input, actions, types)
    return parser.parse()

def format_error(input, offset, expected):
    lines = input.split('\n')
    line_no, position = 0, 0

    while position <= offset:
        position += len(lines[line_no]) + 1
        line_no += 1

    line = lines[line_no - 1]
    message = 'Line ' + str(line_no) + ': expected one of:\n\n'

    for pair in expected:
        message += '    - ' + pair[1] + ' from ' + pair[0] + '\n'

    number = str(line_no)
    while len(number) < 6:
        number = ' ' + number

    message += '\n' + number + ' | ' + line + '\n'
    message += ' ' * (len(line) + 10 + offset - position)
    return message + '^'
