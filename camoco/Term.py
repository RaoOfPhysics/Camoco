#!/usr/bin/python3

import numpy as np

from .Tools import log

class Term(object):
    '''
        A Term is a just group of loci that are related.
    '''
    def __init__(self, id, desc='', loci=None, **kwargs):
        self.id = id
        self.desc = desc
        self.attrs = {}
        self.loci = set()
        if loci:
            self.loci = set(loci)
        for key, val in kwargs.items():
            self.attrs[key] = val

    @property
    def locus_list(self):
        from warnings import warn
        warn('Use self.loci instead of self.locus_list', DeprecationWarning)
        return self.loci

    def __len__(self):
        '''
            Returns the number of loci in the term.
        '''
        return len(self.loci)

    def add_locus(self, locus):
        '''
            Adds a locus to the Term.
        '''
        self.loci.add(locus)

    def flanking_loci(self, gene, window_size=100000):
        '''
            returns any nearby Term SNPs to a gene
        '''
        return [locus for locus in self.loci if abs(gene-locus) <= window_size]

    
    def effective_loci(self, window_size=None):
        '''
            Collapse down loci that have overlapping windows into
            'effective' loci. Looks like:

            Locus1:    |--------o-------|
            Locus2:        |--------o--------|
            Locus3:                         |--------o--------|
            Effective: |--------o---+----------------o--------|

            Legend: '|' : Window edge, used to collapse
                    'o' : 'Locus' edge (SNPs in this case)
                    '+' : Sub loci, kept for downstream analysis

            Parameters
            ----------
            window_size : int (default: None)
                If not None, maps a new window size to each locus.      
        '''
        loci = sorted(self.loci)
        if window_size is not None:
            for locus in loci:
                locus.window = window_size
        collapsed = [loci.pop(0)]
        for locus in loci:
            # if they have overlapping windows, collapse
            if locus in collapsed[-1]:
                # Collapse if the windows overlap
                collapsed[-1] = collapsed[-1] + locus
            else:
                collapsed.append(locus)
        log('{}: Found {} SNPs -> {} effective SNPs', 
            self.id, len(self.loci), len(collapsed)
        )
        return collapsed

    def strongest_loci(self, attr, window_size=None):
        '''
            Collapses down loci that have overlapping windows,
            then returns the locus with the strongest 'attr'
            value. Looks like:

            Locus1:    |--------o-------| (attr: 7)
            Locus2:        |--------o--------| (attr: 2)
            Locus3:                             |--------o--------| (attr: 8)
            Strongest: |--------o-------|       |--------o--------|

            Legend: '|' : Window edge, used to collapse
                    'o' : 'Locus' edge (SNPs in this case)

            Parameters
            ----------
            attr : str
                The locus attribute to use to determine the 'strongest'
            window_size : int (default: None)
                If not None, maps a new window size to each locus.      
        '''
        return [
            # sort by attr and take first item
            sorted(
                locus.sub_loci,
                key=lambda x: float(x.default_getitem(attr,np.inf)),
                reverse=False
            )[0] for locus in self.effective_loci(window_size=window_size)
        ]


    def __str__(self):
        return "Term: {}, Desc: {}, {} Loci".format(self.id, self.desc, len(self))

    def __repr__(self):
        return str(self.id)


