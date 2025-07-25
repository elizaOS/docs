#!/usr/bin/env python3
"""
Comprehensive Link Validation Script for elizaOS Documentation
Extracts and validates all types of links from MDX and MD files
"""

import os
import re
import json
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Set
from urllib.parse import urlparse
import difflib

class LinkValidator:
    def __init__(self, docs_root: str):
        self.docs_root = Path(docs_root)
        self.all_files = set()
        self.links_found = []
        self.broken_links = []
        self.fixes_applied = []
        self.external_links = []
        
        # Build index of all files
        self._build_file_index()
        
    def _build_file_index(self):
        """Build index of all files in the documentation"""
        for pattern in ['**/*.mdx', '**/*.md']:
            for file_path in self.docs_root.glob(pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.docs_root)
                    self.all_files.add(str(relative_path))
                    # Also add without extension for matching
                    self.all_files.add(str(relative_path.with_suffix('')))
                    # Add with leading slash for absolute paths
                    self.all_files.add('/' + str(relative_path))
                    self.all_files.add('/' + str(relative_path.with_suffix('')))
        
    def extract_links_from_file(self, file_path: Path) -> List[Dict]:
        """Extract all types of links from a file"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return []
            
        links = []
        
        # Patterns for different link types
        patterns = [
            # Markdown links [text](url)
            (r'\[([^\]]*)\]\(([^)]+)\)', 'markdown'),
            # href attributes href="url" or href='url'
            (r'href=["\']([^"\']+)["\']', 'href'),
            # src attributes src="url" or src='url'
            (r'src=["\']([^"\']+)["\']', 'src'),
            # Card component hrefs (already covered by href pattern)
        ]
        
        for pattern, link_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if link_type == 'markdown':
                    text, url = match.groups()
                    line_num = content[:match.start()].count('\n') + 1
                    links.append({
                        'file': str(file_path.relative_to(self.docs_root)),
                        'line': line_num,
                        'type': link_type,
                        'text': text,
                        'url': url,
                        'raw_match': match.group(0)
                    })
                else:
                    url = match.group(1)
                    line_num = content[:match.start()].count('\n') + 1
                    links.append({
                        'file': str(file_path.relative_to(self.docs_root)),
                        'line': line_num,
                        'type': link_type,
                        'text': '',
                        'url': url,
                        'raw_match': match.group(0)
                    })
        
        return links
    
    def is_internal_link(self, url: str) -> bool:
        """Check if a URL is an internal link"""
        if url.startswith(('http://', 'https://')):
            return False
        if url.startswith(('mailto:', 'tel:', 'ftp:')):
            return False
        return True
    
    def normalize_internal_path(self, url: str) -> str:
        """Normalize internal path for validation"""
        # Remove fragments and query params
        url = url.split('#')[0].split('?')[0]
        
        # Handle relative paths
        if url.startswith('./'):
            url = url[2:]
        elif url.startswith('../'):
            # For simplicity, treat as potential valid for now
            return url
            
        # Add .mdx extension if not present and no other extension
        if not url.endswith(('.mdx', '.md', '.json', '.png', '.jpg', '.gif', '.svg')):
            url = url + '.mdx'
            
        return url
    
    def find_closest_match(self, target: str) -> str:
        """Find closest matching file for a broken link"""
        target_normalized = target.lower()
        best_matches = difflib.get_close_matches(
            target_normalized, 
            [f.lower() for f in self.all_files], 
            n=3, 
            cutoff=0.6
        )
        
        if best_matches:
            # Find the original case version
            for file_path in self.all_files:
                if file_path.lower() == best_matches[0]:
                    return file_path
        return None
    
    def validate_internal_link(self, link: Dict) -> Dict:
        """Validate an internal link"""
        url = link['url']
        normalized = self.normalize_internal_path(url)
        
        # Check various possible paths
        possible_paths = [
            normalized,
            normalized.lstrip('/'),
            '/' + normalized.lstrip('/'),
            normalized + '.mdx',
            normalized + '.md'
        ]
        
        for path in possible_paths:
            if path in self.all_files:
                return {
                    'valid': True,
                    'target': path,
                    'suggestion': None
                }
        
        # Try to find a close match
        suggestion = self.find_closest_match(normalized)
        
        return {
            'valid': False,
            'target': normalized,
            'suggestion': suggestion
        }
    
    def process_all_files(self):
        """Process all documentation files"""
        for pattern in ['**/*.mdx', '**/*.md']:
            for file_path in self.docs_root.glob(pattern):
                if file_path.is_file():
                    links = self.extract_links_from_file(file_path)
                    
                    for link in links:
                        self.links_found.append(link)
                        
                        if self.is_internal_link(link['url']):
                            validation = self.validate_internal_link(link)
                            if not validation['valid']:
                                self.broken_links.append({
                                    **link,
                                    'validation': validation,
                                    'confidence': 'high' if validation['suggestion'] else 'low'
                                })
                        else:
                            self.external_links.append(link)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        return {
            'summary': {
                'total_files_scanned': len([f for f in self.docs_root.glob('**/*.mdx')] + 
                                         [f for f in self.docs_root.glob('**/*.md')]),
                'total_links_found': len(self.links_found),
                'internal_links': len([l for l in self.links_found if self.is_internal_link(l['url'])]),
                'external_links': len(self.external_links),
                'broken_internal_links': len(self.broken_links),
                'fixes_applied': len(self.fixes_applied)
            },
            'broken_links': self.broken_links,
            'external_links': self.external_links,
            'fixes_applied': self.fixes_applied,
            'all_links': self.links_found
        }

if __name__ == '__main__':
    validator = LinkValidator('/home/runner/work/docs/docs')
    validator.process_all_files()
    report = validator.generate_report()
    
    with open('/home/runner/work/docs/docs/link_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Link validation complete!")
    print(f"Total links found: {report['summary']['total_links_found']}")
    print(f"Broken internal links: {report['summary']['broken_internal_links']}")
    print(f"External links: {report['summary']['external_links']}")