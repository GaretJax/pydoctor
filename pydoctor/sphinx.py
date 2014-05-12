"""
Support for Sphinx compatibility.
"""
from __future__ import absolute_import
import os
import zlib


class SphinxInventory(object):
    """
    Sphinx inventory handler.
    """

    version = (2, 0)

    def __init__(self, logger, project_name):
        self.project_name = project_name
        self.msg = logger

    def generate(self, subjects, basepath):
        """
        Generate Sphinx objects inventory version 2 at `basepath`/objects.inv.
        """
        path = os.path.join(basepath, 'objects.inv')
        self.msg('sphinx', 'Generating objects inventory at %s' % (path,))

        with self._openFileForWriting(path) as target:
            target.write(self._generateHeader())
            content = self._generateContent(subjects)
            target.write(zlib.compress(content))

    def _openFileForWriting(self, path):
        """
        Helper for testing.
        """
        return open(path, 'w')

    def _generateHeader(self):
        """
        Return header for project  with name.
        """
        version = [str(part) for part in self.version]
        return """# Sphinx inventory version 2
# Project: %s
# Version: %s
# The rest of this file is compressed with zlib.
""" % (self.project_name, '.'.join(version))

    def _generateContent(self, subjects):
        """
        Write inventory for all `subjects`.
        """
        content = []
        for obj in subjects:
            content.append(self._generateLine(obj))
            content.append(self._generateContent(obj.orderedcontents))

        return ''.join(content)

    def _generateLine(self, obj):
        """
        Return inventory line for object.

        name domain_name:type priority URL display_name

        Domain name is always: py
        Priority is always: -1
        Display name is always: -
        """
        full_name = obj.fullName()
        full_parent_name = ''
        if obj.parent:
            full_parent_name = obj.parent.fullName()
        display = '-'
        mapping = {
            'package': ('module', full_name, None),
            'module': ('module', full_name, None),
            'class': ('class', full_name, None),
            'method': ('method', full_parent_name, obj.name),
            'function': ('function', full_parent_name, obj.name),
            'attribute': ('attribute', full_parent_name, obj.name),
            }

        try:
            domainname, base_url, anchor = mapping[obj.kind.lower()]
        except (KeyError, AttributeError):
            domainname = 'obj'
            base_url = full_name
            anchor = None
            self.msg('sphinx', "Unknown type for %s." % (full_name,))

        base_url += '.html'
        if anchor:
            url = '%s#%s' % (base_url, anchor)
        else:
            url = base_url

        return '%s py:%s -1 %s %s\n' % (full_name, domainname, url, display)
