import config
from disasm import Types
from utils.ail_utils import ELF_utils, set_loc, get_loc


if ELF_utils.elf_64():
    # x86_64

    cslab = Types.Label(config.gfree_cookiestackvar + '@tpoff')

    returnenc = [
        Types.DoubleInstr(('pushq', Types.RegClass('rax'), None, False)),
        Types.TripleInstr(('movq', Types.RegClass('rax'), Types.Label(config.gfree_xorkeyvar), None, False)),
        Types.TripleInstr(('xorq', Types.BinOP_PLUS((Types.RegClass('rsp'), 8)), Types.RegClass('rax'), None, False)),
        Types.DoubleInstr(('popq', Types.RegClass('rax'), None, False)),
    ]

    framecookiehead = [
        Types.DoubleInstr(('pushq', Types.RegClass('rax'), None, False)),
        Types.DoubleInstr(('pushq', Types.RegClass('rbx'), None, False)),
        Types.TripleInstr(('addq', Types.SegRef(('fs', cslab)), Types.Normal(1), None, False)),
        Types.TripleInstr(('movq', Types.RegClass('rbx'), Types.SegRef(('fs', cslab)), None, False)),
        Types.TripleInstr(('movq', Types.RegClass('rax'), Types.Label(config.gfree_cookiekeyvar), None, False)),
        ['xorq', Types.RegClass('rax'), None, None, False], # Fill with FuncID
        Types.TripleInstr(('xorq', Types.RegClass('rax'), Types.RegClass('rbx'), None, False)),
        Types.TripleInstr(('movq', Types.SegRef(('fs', Types.JmpTable_PLUS_S((cslab, Types.RegClass('rbx'), 8)))), Types.RegClass('rax'), None, False)),
        Types.DoubleInstr(('popq', Types.RegClass('rbx'), None, False)),
        Types.DoubleInstr(('popq', Types.RegClass('rax'), None, False)),
    ]

    framecookiecheck = [
        Types.DoubleInstr(('pushq', Types.RegClass('rax'), None, False)),
        Types.TripleInstr(('movq', Types.RegClass('rax'), Types.SegRef(('fs', cslab)), None, False)),
        Types.TripleInstr(('xorq', Types.RegClass('rax'), Types.SegRef(('fs', Types.JmpTable_PLUS_S((cslab, Types.RegClass('rax'), 8)))), None, False)),
        ['xorq', Types.RegClass('rax'), None, None, False], # Fill with FuncID
        Types.TripleInstr(('cmpq', Types.RegClass('rax'), Types.Label(config.gfree_cookiekeyvar), None, False)),
        Types.DoubleInstr(('popq', Types.RegClass('rax'), None, False)),
        Types.DoubleInstr(('jne', Types.Label(config.gfree_failfuncname), None, False))
    ]

    framecookietail = [
        Types.TripleInstr(('subq', Types.SegRef(('fs', cslab)), Types.Normal(1), None, False))
    ]

elif ELF_utils.elf_arm():
    # ARM

    returnenc = [
        Types.DoubleInstr(('push', Types.RegList((Types.RegClass('r0'),)), None, False)),
        Types.TripleInstr(('movw', Types.RegClass('r0'), Types.Label('#:lower16:' + config.gfree_xorkeyvar), None, False)),
        Types.TripleInstr(('movt', Types.RegClass('r0'), Types.Label('#:upper16:' + config.gfree_xorkeyvar), None, False)),
        Types.TripleInstr(('ldr', Types.RegClass('r0'), Types.UnOP('r0'), None, False)),
        Types.TripleInstr(('eor', Types.RegClass('lr'), Types.RegClass('r0'), None, False)),
        Types.DoubleInstr(('pop', Types.RegList((Types.RegClass('r0'),)), None, False))
    ]

    framecookiehead = [
        Types.DoubleInstr(('push', Types.RegList((Types.RegClass('r0'), Types.RegClass('r1'), Types.RegClass('r2'))), None, False)),
        Types.CoproInstr(('mrc', Types.Label('p15'), Types.Label('0'), Types.RegClass('r2'), Types.RegClass('c13'), Types.RegClass('c0'), Types.Label('3'), None, False)),
        Types.TripleInstr(('movw', Types.RegClass('r1'), Types.Label('#:lower16:.LC3'), None, False)),
        Types.TripleInstr(('movt', Types.RegClass('r1'), Types.Label('#:upper16:.LC3'), None, False)),
        Types.TripleInstr(('ldr', Types.RegClass('r1'), Types.UnOP('r1'), None, False)),
        Types.TripleInstr(('add', Types.RegClass('r2'), Types.RegClass('r1'), None, False)),
        Types.TripleInstr(('movw', Types.RegClass('r0'), Types.Label('#:lower16:' + config.gfree_cookiekeyvar), None, False)),
        Types.TripleInstr(('movt', Types.RegClass('r0'), Types.Label('#:upper16:' + config.gfree_cookiekeyvar), None, False)),
        Types.TripleInstr(('ldr', Types.RegClass('r0'), Types.UnOP('r0'), None, False)),
        ['movw', Types.RegClass('r1'), None, None, False], # Fill with FuncID
        ['movt', Types.RegClass('r1'), None, None, False], # Fill with FuncID
        Types.TripleInstr(('eors', Types.RegClass('r0'), Types.RegClass('r1'), None, False)),
        Types.TripleInstr(('ldr', Types.RegClass('r1'), Types.UnOP('r2'), None, False)),
        Types.TripleInstr(('adds', Types.RegClass('r1'), Types.Normal(1), None, False)),
        Types.TripleInstr(('str', Types.RegClass('r1'), Types.UnOP('r2'), None, False)),
        Types.TripleInstr(('eors', Types.RegClass('r0'), Types.RegClass('r1'), None, False)),
        Types.TripleInstr(('str', Types.RegClass('r0'), Types.ThreeOP((Types.RegClass('r2'), Types.RegClass('r1'), Types.ShiftExp('lsl', 2))), None, False)),
        Types.DoubleInstr(('pop', Types.RegList((Types.RegClass('r0'), Types.RegClass('r1'), Types.RegClass('r2'))), None, False)),
    ]

    framecookiecheck = [
        Types.DoubleInstr(('push', Types.RegList((Types.RegClass('r0'), Types.RegClass('r1'))), None, False)),
        Types.CoproInstr(('mrc', Types.Label('p15'), Types.Label('0'), Types.RegClass('r0'), Types.RegClass('c13'), Types.RegClass('c0'), Types.Label('3'), None, False)),
        Types.TripleInstr(('movw', Types.RegClass('r1'), Types.Label('#:lower16:.LC3'), None, False)),
        Types.TripleInstr(('movt', Types.RegClass('r1'), Types.Label('#:upper16:.LC3'), None, False)),
        Types.TripleInstr(('ldr', Types.RegClass('r1'), Types.UnOP('r1'), None, False)),
        Types.TripleInstr(('adds', Types.RegClass('r0'), Types.RegClass('r1'), None, False)),
        Types.TripleInstr(('ldr', Types.RegClass('r1'), Types.UnOP('r0'), None, False)),
        Types.TripleInstr(('ldr', Types.RegClass('r0'), Types.ThreeOP((Types.RegClass('r0'), Types.RegClass('r1'), Types.ShiftExp('lsl', 2))), None, False)),
        Types.TripleInstr(('eors', Types.RegClass('r0'), Types.RegClass('r1'), None, False)),
        ['movw', Types.RegClass('r1'), None, None, False], # Fill with FuncID
        ['movt', Types.RegClass('r1'), None, None, False], # Fill with FuncID
        Types.TripleInstr(('eors', Types.RegClass('r0'), Types.RegClass('r1'), None, False)),
        Types.TripleInstr(('movw', Types.RegClass('r1'), Types.Label('#:lower16:' + config.gfree_cookiekeyvar), None, False)),
        Types.TripleInstr(('movt', Types.RegClass('r1'), Types.Label('#:upper16:' + config.gfree_cookiekeyvar), None, False)),
        Types.TripleInstr(('ldr', Types.RegClass('r1'), Types.UnOP('r1'), None, False)),
        Types.TripleInstr(('cmp', Types.RegClass('r0'), Types.RegClass('r1'), None, False)),
        Types.DoubleInstr(('bne', Types.Label(config.gfree_failfuncname), None, False)),
        Types.TripleInstr(('movw', Types.RegClass('r0'), Types.Label('#:lower16:.text-1'), None, False)),
        Types.TripleInstr(('movt', Types.RegClass('r0'), Types.Label('#:upper16:.text'), None, False)),
        ['cmp', None, Types.RegClass('r0'), None, False],  # Fill with call register
        Types.DoubleInstr(('pop', Types.RegList((Types.RegClass('r0'), Types.RegClass('r1'))), None, False)),
        Types.DoubleInstr(('it', Types.Label('hi'), None, False)),
        ['orrhi', None, Types.Normal(1), None, False]      # Fill with call register
    ]

    framecookietail = [
        Types.DoubleInstr(('push', Types.RegList((Types.RegClass('r0'), Types.RegClass('r1'))), None, False)),
        Types.CoproInstr(('mrc', Types.Label('p15'), Types.Label('0'), Types.RegClass('r1'), Types.RegClass('c13'), Types.RegClass('c0'), Types.Label('3'), None, False)),
        Types.TripleInstr(('movw', Types.RegClass('r0'), Types.Label('#:lower16:.LC3'), None, False)),
        Types.TripleInstr(('movt', Types.RegClass('r0'), Types.Label('#:upper16:.LC3'), None, False)),
        Types.TripleInstr(('ldr', Types.RegClass('r0'), Types.UnOP('r0'), None, False)),
        Types.TripleInstr(('add', Types.RegClass('r1'), Types.RegClass('r0'), None, False)),
        Types.TripleInstr(('ldr', Types.RegClass('r0'), Types.UnOP('r1'), None, False)),
        Types.TripleInstr(('subs', Types.RegClass('r0'), Types.Normal(1), None, False)),
        Types.TripleInstr(('str', Types.RegClass('r0'), Types.UnOP('r1'), None, False)),
        Types.DoubleInstr(('pop', Types.RegList((Types.RegClass('r0'), Types.RegClass('r1'))), None, False)),
    ]

else:
    # x86_32

    cslab = Types.Label(config.gfree_cookiestackvar + '@ntpoff')

    returnenc = [
        Types.DoubleInstr(('pushl', Types.RegClass('eax'), None, False)),
        Types.TripleInstr(('movl', Types.RegClass('eax'), Types.Label(config.gfree_xorkeyvar), None, False)),
        Types.TripleInstr(('xorl', Types.BinOP_PLUS((Types.RegClass('esp'), 4)), Types.RegClass('eax'), None, False)),
        Types.DoubleInstr(('popl', Types.RegClass('eax'), None, False)),
    ]

    framecookiehead = [
        Types.DoubleInstr(('pushl', Types.RegClass('eax'), None, False)),
        Types.DoubleInstr(('pushl', Types.RegClass('ebx'), None, False)),
        Types.TripleInstr(('addl', Types.SegRef(('gs', cslab)), Types.Normal(1), None, False)),
        Types.TripleInstr(('movl', Types.RegClass('ebx'), Types.SegRef(('gs', cslab)), None, False)),
        Types.TripleInstr(('movl', Types.RegClass('eax'), Types.Label(config.gfree_cookiekeyvar), None, False)),
        ['xorl', Types.RegClass('eax'), None, None, False], # Fill with FuncID
        Types.TripleInstr(('xorl', Types.RegClass('eax'), Types.RegClass('ebx'), None, False)),
        Types.TripleInstr(('movl', Types.SegRef(('gs', Types.JmpTable_PLUS_S((cslab, Types.RegClass('ebx'), 4)))), Types.RegClass('eax'), None, False)),
        Types.DoubleInstr(('popl', Types.RegClass('ebx'), None, False)),
        Types.DoubleInstr(('popl', Types.RegClass('eax'), None, False)),
    ]

    framecookiecheck = [
        Types.DoubleInstr(('pushl', Types.RegClass('eax'), None, False)),
        Types.TripleInstr(('movl', Types.RegClass('eax'), Types.SegRef(('gs', cslab)), None, False)),
        Types.TripleInstr(('xorl', Types.RegClass('eax'), Types.SegRef(('gs', Types.JmpTable_PLUS_S((cslab, Types.RegClass('eax'), 4)))), None, False)),
        ['xorl', Types.RegClass('eax'), None, None, False], # Fill with FuncID
        Types.TripleInstr(('cmpl', Types.RegClass('eax'), Types.Label(config.gfree_cookiekeyvar), None, False)),
        Types.DoubleInstr(('popl', Types.RegClass('eax'), None, False)),
        Types.DoubleInstr(('jne', Types.Label(config.gfree_failfuncname), None, False))
    ]

    framecookietail = [
        Types.TripleInstr(('subl', Types.SegRef(('gs', cslab)), Types.Normal(1), None, False))
    ]


def set_inlineblocklocation(loc, block):
    return [set_loc(block[0], loc)] + \
        map(lambda i: set_loc(i, Types.Loc('', loc.loc_addr, loc.loc_visible)), block[1:])


if ELF_utils.elf_arm():
    # ARM
    def get_returnenc(curr_instr, popcookie=False):
        pre = list(framecookietail) if popcookie else []
        loc = get_loc(curr_instr)
        if curr_instr[0].upper().startswith('POP'):
            i = map(str.upper, curr_instr[1]).index('PC')
            rlist = curr_instr[1][:i] + ('lr',) + curr_instr[1][i+1:]
            pre.insert(0, Types.DoubleInstr((curr_instr[0], Types.RegList(rlist), None, False)))
            curr_instr = Types.DoubleInstr(('bx', Types.RegClass('lr'), None, False))
        elif curr_instr[0].upper().startswith('LDR') and curr_instr[1].upper() == 'PC':
            pre.insert(0, type(curr_instr)((curr_instr[0], Types.RegClass('lr')) + curr_instr[2:]))
            curr_instr = Types.DoubleInstr(('bx', Types.RegClass('lr'), None, False))
        return set_inlineblocklocation(loc, pre + returnenc) + \
               [set_loc(curr_instr, Types.Loc('', loc.loc_addr, loc.loc_visible))]

    def get_framecookiehead(curr_instr, funcID):
        loc = get_loc(curr_instr)
        tmp = list(framecookiehead)
        tmp[9][2] = Types.Normal(funcID[0])
        tmp[10][2] = Types.Normal(funcID[1])
        tmp[9] = Types.TripleInstr(tmp[9])
        tmp[10] = Types.TripleInstr(tmp[10])
        return set_inlineblocklocation(loc, returnenc + tmp) + \
               [set_loc(curr_instr, Types.Loc('', loc.loc_addr, loc.loc_visible))]

    def get_framecookiecheck(curr_instr, funcID):
        loc = get_loc(curr_instr)
        tmp = list(framecookiecheck)
        tmp[9][2] = Types.Normal(funcID[0])
        tmp[10][2] = Types.Normal(funcID[1])
        tmp[-4][1] = curr_instr[1]
        tmp[-1][1] = curr_instr[1]
        tmp[9] = Types.TripleInstr(tmp[9])
        tmp[10] = Types.TripleInstr(tmp[10])
        tmp[-4] = Types.TripleInstr(tmp[-4])
        tmp[-1] = Types.TripleInstr(tmp[-1])
        return set_inlineblocklocation(loc, tmp) + \
               [set_loc(curr_instr, Types.Loc('', loc.loc_addr, loc.loc_visible))]

else:
    # x86
    def get_returnenc(curr_instr, popcookie=False):
        loc = get_loc(curr_instr)
        return set_inlineblocklocation(loc, framecookietail + returnenc if popcookie else returnenc) + \
               [set_loc(curr_instr, Types.Loc('', loc.loc_addr, loc.loc_visible))]

    def get_framecookiehead(curr_instr, funcID):
        loc = get_loc(curr_instr)
        tmp = list(framecookiehead)
        tmp[5][2] = Types.Normal(funcID)
        tmp[5] = Types.TripleInstr(tmp[5])
        return set_inlineblocklocation(loc, returnenc + tmp) + \
               [set_loc(curr_instr, Types.Loc('', loc.loc_addr, loc.loc_visible))]

    def get_framecookiecheck(curr_instr, funcID):
        loc = get_loc(curr_instr)
        tmp = list(framecookiecheck)
        tmp[3][2] = Types.Normal(funcID)
        tmp[3] = Types.TripleInstr(tmp[3])
        return set_inlineblocklocation(loc, tmp) + \
               [set_loc(curr_instr, Types.Loc('', loc.loc_addr, loc.loc_visible))]