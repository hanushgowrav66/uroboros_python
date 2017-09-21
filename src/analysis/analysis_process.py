from cg import cg
from cfg import cfg
from utils.ail_utils import read_file, ELF_utils
from utils.pp_print import pp_print_list, pp_print_file

class Analysis(object):

    @staticmethod
    def global_bss():
        lines = read_file('globalbss.info')
        def mapper(l):
            items = l.strip().split()
            return (items[0][1:].upper(), items[1])
        return map(mapper, lines)

    @staticmethod
    def analyze_one(il, fl, re, docfg=False):
        u_fl = filter(lambda f: not f.is_lib, fl)

        if docfg:
            _cg = cg()
            _cg.set_funcs(fl)
            il = _cg.visit(il)

        il = re.adjust_loclabel(il)
        re.reassemble_dump(u_fl)
        il = re.adjust_jmpref(il)

        if docfg:
            _cfg = cfg()
            _cfg.set_funcs(fl)
            il = _cfg.visit(il)
            bbl = _cfg.get_bbl()
            il = re.add_bblock_label(bbl, il)
            return (_cfg.get_fbl(), bbl, _cfg.get_cfg_table(il), _cg.get_cg_table(), il, re)

        return (None, None, None, None, il, re)

    @staticmethod
    def post_analyze(il, re):
        il = re.unify_loc(il)
        if ELF_utils.elf_arm(): il = re.alignvldrARM(il)
        ils = pp_print_list(il)
        ils = re.adjust_globallabel(Analysis.global_bss(), ils)
        pp_print_file(ils)
