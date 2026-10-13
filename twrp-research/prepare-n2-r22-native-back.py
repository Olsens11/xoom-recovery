from pathlib import Path
root=Path("/home/ps2/xoom-phase1/twrp-research/TeamWin-recovery-7.1-src/gui")
action=root/"action.cpp"
hpp=root/"objects.hpp"
a=action.read_text()
h=hpp.read_text()
assert "xoomnetworkback" not in a+h
anchor="\t\tADD_ACTION(xoomwifiprofile);"
assert a.count(anchor)==1
a=a.replace(anchor,anchor+"\n\t\tADD_ACTION(xoomnetworkback);",1)
anchor="int GUIAction::xoomwifiprofile(std::string arg)"
assert a.count(anchor)==1
new="""// Network page only: react to an actual Back keypress rather than a
// conditional GUIAction whose NotifyVarChange can auto-trigger navigation.
int GUIAction::xoomnetworkback(std::string arg)
{
    (void)arg;
    std::string visible;
    DataManager::GetValue("xoom_n2_keyboard_visible", visible);
    if (visible == "1") {
        DataManager::SetValue("xoom_n2_focus_target", "");
        DataManager::SetValue("xoom_n2_keyboard_visible", "0");
        return 0;
    }
    return gui_changePage("advanced");
}

"""
a=a.replace(anchor,new+anchor,1)
anchor="\tint xoomwifiprofile(std::string arg);"
assert h.count(anchor)==1
h=h.replace(anchor,anchor+"\n\tint xoomnetworkback(std::string arg);",1)
action.write_text(a)
hpp.write_text(h)
print("NATIVE_BACK_PATCH_READY action lines",len(a.splitlines()),"hpp lines",len(h.splitlines()))
