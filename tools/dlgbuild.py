"""Reusable TSL DLG (conversation) generator. Produces a valid 'DLG V3.2' tree.

Author conversations as entries (NPC lines) and replies (player lines) linked by
list index; text is referenced by dialog.tlk StrRef (use tools/tlk.py to append).
"""
from gfftool import Struct, write
# GFF type ids
B,W,I,DW,F,EXO,RES,LOC,LIST = 0,2,5,4,8,10,11,12,15

def _link(index, is_child=0, link_comment=False):
    s = Struct(0); f = s.fields
    f["Index"] = (DW, index)
    f["Active"] = (RES, ""); f["Active2"] = (RES, "")
    for n in range(1,6): f["Param%d"%n] = (I,0)
    for n in range(1,6): f["Param%db"%n] = (I,0)
    f["Not"] = (B,0); f["Not2"] = (B,0); f["Logic"] = (I,0)
    f["ParamStrA"] = (EXO,""); f["ParamStrB"] = (EXO,"")
    f["IsChild"] = (B, is_child)
    if link_comment: f["LinkComment"] = (EXO,"")
    return s

def _common(f):
    f["VO_ResRef"] = (RES,""); f["Script"] = (RES,""); f["Script2"] = (RES,"")
    for n in range(1,6): f["ActionParam%d"%n] = (I,0)
    for n in range(1,6): f["ActionParam%db"%n] = (I,0)
    f["ActionParamStrA"] = (EXO,""); f["ActionParamStrB"] = (EXO,"")
    f["NodeUnskippable"] = (I,0); f["Delay"] = (DW,0xFFFFFFFF); f["Comment"] = (EXO,"")
    f["Sound"] = (RES,""); f["Quest"] = (EXO,""); f["PlotIndex"] = (I,-1)
    f["PlotXPPercentage"] = (F,1.0); f["PostProcNode"] = (I,0); f["AlienRaceNode"] = (I,0)
    f["Emotion"] = (I,0); f["RecordVO"] = (I,0); f["RecordNoVOOverri"] = (I,0)
    f["FacialAnim"] = (I,0); f["Listener"] = (EXO,""); f["WaitFlags"] = (DW,0)
    f["CameraAngle"] = (DW,0); f["CamVidEffect"] = (I,-1); f["FadeType"] = (B,0)

def entry(node_id, text_strref, reply_indices, script=""):
    s = Struct(0); f = s.fields
    f["Speaker"] = (EXO,""); f["AnimList"] = (LIST,[]); f["Text"] = (LOC,(text_strref,[]))
    _common(f)
    f["Script"] = (RES, script)
    f["NodeID"] = (I, node_id)
    f["VOTextChanged"] = (B,0); f["Changed"] = (B,0)
    f["RepliesList"] = (LIST, [_link(i) for i in reply_indices])
    f["SoundExists"] = (B,0)
    return s

def reply(text_strref, entry_indices, script=""):
    s = Struct(0); f = s.fields
    f["AnimList"] = (LIST,[]); f["Text"] = (LOC,(text_strref,[]))
    _common(f)
    f["Script"] = (RES, script)
    f["EntriesList"] = (LIST, [_link(i, is_child=1, link_comment=True) for i in entry_indices])
    return s

def build_dlg(entries, replies, starting_indices, vo_id="", end_script=""):
    s = Struct(-1); f = s.fields
    f["DelayEntry"] = (DW,0); f["DelayReply"] = (DW,0); f["NumWords"] = (DW,0)
    # end_script fires when the conversation closes normally (reliable for StartNewModule etc.)
    f["EndConversation"] = (RES,end_script); f["EndConverAbort"] = (RES,""); f["Skippable"] = (B,1)
    f["StuntList"] = (LIST,[]); f["CameraModel"] = (RES,""); f["VO_ID"] = (EXO,vo_id)
    f["ConversationType"] = (I,0); f["ComputerType"] = (B,0); f["OldHitCheck"] = (B,0)
    f["AmbientTrack"] = (RES,""); f["UnequipItems"] = (B,0); f["AnimatedCut"] = (B,0)
    f["UnequipHItem"] = (B,0); f["NextNodeID"] = (I,len(entries)); f["DeletedVOFiles"] = (EXO,"")
    f["PostProcOwner"] = (I,0); f["AlienRaceOwner"] = (I,0); f["RecordNoVO"] = (I,0)
    f["EntryList"] = (LIST, entries)
    f["ReplyList"] = (LIST, replies)
    f["StartingList"] = (LIST, [_link(i) for i in starting_indices])
    return s

def write_dlg(path, entries, replies, starting_indices, vo_id="", end_script=""):
    return write(path, "DLG ", "V3.2", build_dlg(entries, replies, starting_indices, vo_id, end_script))
