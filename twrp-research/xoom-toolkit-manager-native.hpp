#pragma once
#include <string>
// Recovery-owned Toolkit UI and manual lifecycle backend (R22d4).
void XoomToolkit_Refresh();
void XoomToolkit_NormalizeAutostart();
int XoomToolkit_ChangeMode(const std::string &mode);
int XoomToolkit_Action(const std::string &action);
int XoomToolkit_Execute(const std::string &action);
