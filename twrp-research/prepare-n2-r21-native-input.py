#!/usr/bin/env python3
"""N2 only, local TWRP GUIInput keyboard focus; emit inspectable source diff."""
from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research/TeamWin-recovery-7.1-src/gui/input.cpp")
s=p.read_text()
assert "xoom_n2_keyboard_visible" not in s
anchor='''	if (!HasInputFocus) {
		if (state != TOUCH_RELEASE)'''
assert s.count(anchor)==1
addition='''	// Xoom N2: explicit focus for the two Network fields, independent of
	// their declaration/render order. Do not change other recovery inputs.
	// Only a real touch in a Network input opens the on-screen keyboard.
	if ((mVariable == "xoom_n2_ssid" || mVariable == "xoom_n2_password") &&
	    state == TOUCH_RELEASE && GetSelection(x, y) >= 0) {
		PageManager::SetKeyBoardFocus(0);
		PageManager::NotifyCharInput(0);
		DataManager::SetValue("xoom_n2_focus_target", mVariable);
		SetInputFocus(1);
		DrawCursor = true;
		HandleCursorByTouch(x);
		mRendered = false;
		DataManager::SetValue("xoom_n2_keyboard_visible", "1");
		return 0;
	}
'''
s=s.replace(anchor,addition+anchor,1)
anchor='''	GUIObject::NotifyVarChange(varName, value);

	if (varName == mVariable) {'''
assert s.count(anchor)==1
addition='''	GUIObject::NotifyVarChange(varName, value);

	// Enter on the SSID field switches focus to password, without a page
	// reload. Enter on password hides keyboard without connecting.
	if (varName == "xoom_n2_focus_target" &&
	    (mVariable == "xoom_n2_ssid" || mVariable == "xoom_n2_password")) {
		const bool focused = (value == mVariable);
		SetInputFocus(focused ? 1 : 0);
		DrawCursor = focused;
		mRendered = false;
		if (focused)
			HandleCursorByText();
		return 0;
	}

	if (varName == mVariable) {'''
s=s.replace(anchor,addition,1)
anchor='''	if (HasInputFocus) {
		if (key == KEYBOARD_BACKSPACE) {'''
assert s.count(anchor)==1
replacement='''	if (HasInputFocus) {
		if (key == KEYBOARD_ACTION &&
		    (mVariable == "xoom_n2_ssid" || mVariable == "xoom_n2_password")) {
			if (mVariable == "xoom_n2_ssid") {
				DataManager::SetValue("xoom_n2_focus_target", "xoom_n2_password");
				DataManager::SetValue("xoom_n2_keyboard_visible", "1");
			} else {
				DataManager::SetValue("xoom_n2_focus_target", "");
				DataManager::SetValue("xoom_n2_keyboard_visible", "0");
			}
			// Deliberately do not call the field's old <action function=page>
			// or the network Connect action.
			return 0;
		}
		if (key == KEYBOARD_BACKSPACE) {'''
s=s.replace(anchor,replacement,1)
p.write_text(s)
print("N2 native GUIInput inserted, lines",len(s.splitlines()))
