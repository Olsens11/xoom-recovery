#!/usr/bin/env python3
"""Future-only package Help standard for XoomToolkit (R22d4c is immutable).

Exact 1920x1200 TWRP theme-unit Help button reused from the frozen R22d4c
main Toolkit; generates package-specific pages from concise documented content.
No direct commands, scripts, credentials or new runtime behaviour.
"""
from pathlib import Path
import io
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
TIME = HERE / "XoomToolkit-Time-Sync-0.2.0-FUTURE-TWRP-page.xml"
LOGS = HERE / "XoomToolkit-Recovery-Log-Collector-0.1.0-FUTURE-TWRP-page.xml"
DIAG = HERE / "XoomToolkit-Advanced-Network-Diagnostics-0.2.0-FUTURE-TWRP-page.xml"
INSPECT = HERE / "XoomToolkit-Partition-Storage-Inspector-0.1.0-FUTURE-TWRP-page.xml"
EXISTING = HERE / "XoomToolkit-Existing-Packages-Help-FUTURE-pages.xml"
BUTTON = {"x":"1672","y":"34","w":"156","h":"69"}
BLUE = "#1c75a8"
WHITE = "#ffffff"

# Section headings and help text are structured identically on every page.
# Keep rows brief: font_s on 1280x800 physical pixels, 1920x1200 theme units.
CONTENT = {
  "xoom_toolkit_details_time_sync": {
    "title": "Time Sync Help",
    "entries": [
      ("PURPOSE", "Keeps the recovery clock accurate and displays local time."),
      ("REQUIRES", "Time synchronization needs Wi-Fi and access to an NTP server."),
      ("CONTROLS", "Sync Now makes a bounded NTP request; Refresh updates the time."),
      ("", "Change Time Zone opens the existing TWRP settings picker."),
      ("TIME ZONE", "Save zone, quarter-hour offset and daylight-saving choice."),
      ("", "The saved choice is restored even if Wi-Fi is unavailable."),
      ("AUTORUN", "Autoload loads the module; Autorun syncs once after Wi-Fi is ready."),
      ("", "No permanent NTP daemon or connection polling is started."),
      ("IF IT FAILS", "If the network is offline, wait for Wi-Fi or use Sync Now."),
      ("SAFETY", "NTP sets UTC; the chosen zone sets the local clock display."),
      ("", "No Android partition or saved Wi-Fi profile is modified."),
    ],
  },
  "xoom_toolkit_details_log_collector": {
    "title": "Recovery Log Collector Help",
    "entries": [
      ("PURPOSE", "Creates a small diagnostic report for recovery problems."),
      ("REQUIRES", "The package must be loaded; internet access is not needed."),
      ("COLLECT", "Collect Report builds a sanitized snapshot in recovery RAM."),
      ("", "It includes known states, transitions and warning/error counts."),
      ("EXPORT", "Export to SD saves the latest report only when requested."),
      ("", "A verified, writable microSD card is required for exporting."),
      ("STARTUP", "Autoload loads the module; Autorun is optional, not required."),
      ("", "Early boot collection may miss later problems; collect again."),
      ("PRIVACY", "The default report excludes raw Wi-Fi profiles and log lines."),
      ("", "Review the report before sending it to someone else."),
      ("IF IT FAILS", "Missing log sources are reported as unavailable."),
    ],
  },
  "xoom_toolkit_details_partition_inspector": {
    "title": "Partition & Storage Inspector Help",
    "entries": [
      ("PURPOSE", "Shows storage devices and partition layout without writing."),
      ("REQUIRES", "A loaded module. No Wi-Fi connection is needed."),
      ("CONTROLS", "Inspect Storage records sysfs and /proc metadata to RAM."),
      ("", "Export Report to SD is a separate, explicit operation."),
      ("DEVICES", "On this Xoom, mmcblk0 is expected SD; mmcblk1 is eMMC."),
      ("", "Recovery p6 is only verified when its by-name link resolves."),
      ("MOUNTS", "A direct-path mount match is reported; absence is uncertain."),
      ("STARTUP", "Autoload loads the module; optional Autorun can inspect."),
      ("SAFETY", "This package never opens /dev/block device contents."),
      ("", "It cannot partition, format, mount, write, repair or flash."),
      ("IF IT FAILS", "Missing or suspicious metadata is marked unknown."),
    ],
  },
  "xoom_network": {
    "title": "Wi-Fi Runtime Help",
    "entries": [
      ("PURPOSE", "Enables recovery Wi-Fi for tools, diagnostics and time sync."),
      ("REQUIRES", "The verified Wi-Fi Runtime module must be loaded."),
      ("CONTROLS", "Use the Network screen to connect or disconnect Wi-Fi."),
      ("", "The Network details show current status and IPv4 when available."),
      ("STARTUP", "Autoload restores the runtime from the SD package."),
      ("", "Network Autoconnect needs a previously saved Wi-Fi profile."),
      ("", "Autorun and Autoconnect are independent settings."),
      ("IF IT FAILS", "Check WPA authentication, DHCP and Network Diagnostics."),
      ("SAFETY", "Saved Wi-Fi profiles on FAT32 are not encrypted."),
      ("", "Never export credentials as part of ordinary diagnostics."),
      ("", "Wireless ADB is separate and is not enabled by Wi-Fi."),
    ],
  },
  "xoom_toolkit_details_diag": {
    "title": "Network Diagnostics Help",
    "entries": [
      ("PURPOSE", "Inspects recovery Wi-Fi, routing, DNS, and connection health."),
      ("REQUIRES", "Wi-Fi Runtime must be loaded before Diagnostics can load."),
      ("CONTROLS", "Inspect Network creates a passive status report in RAM."),
      ("", "Test Connectivity makes bounded ping and DNS requests."),
      ("STARTUP", "Autoload loads the module after the Wi-Fi dependency."),
      ("", "Autorun, if enabled, only runs the passive inspection."),
      ("", "The module does not need to run as a permanent daemon."),
      ("IF IT FAILS", "Blocked ICMP or missing DNS tools do not prove an outage."),
      ("SAFETY", "No recurring pollers, Wi-Fi setting changes, or raw credentials."),
      ("", "Export Report copies the current summary to SD on request."),
      ("", "The DNS test does not verify the Bionic DNS proxy itself."),
    ],
  },
  "xoom_toolkit_details_poc": {
    "title": "Wireless ADB POC Help",
    "entries": [
      ("PURPOSE", "Explains the experimental wireless ADB placeholder."),
      ("STATUS", "This proof-of-concept is unavailable in R22d4c."),
      ("", "There is no wireless ADB listener in this package."),
      ("CONTROLS", "No Start or Stop action is available for this placeholder."),
      ("", "USB ADB remains managed by normal TWRP."),
      ("SAFETY", "Unauthenticated TCP ADB can expose root access on the LAN."),
      ("", "It must require explicit approval and an obvious OFF control."),
      ("", "Never enable it automatically or preserve it across reboots."),
      ("FUTURE", "Temporary insecure ADB and authenticated ADB are distinct."),
      ("", "Only a later tested recovery may offer these capabilities."),
    ],
  },
}

def add_text(page, text, x, y, color="%text_color%", font="font_s"):
    el=ET.SubElement(page, "text")
    ET.SubElement(el, "placement", {"x":str(x),"y":str(y)})
    ET.SubElement(el, "font", {"resource":font,"color":color})
    ET.SubElement(el, "text").text=text
    return el

def add_button(page, label, coords, destination, color=BLUE):
    button=ET.Element("button")
    ET.SubElement(button,"placement",coords)
    ET.SubElement(button,"fill",{"color":color})
    ET.SubElement(button,"font",{"resource":"font_s","color":WHITE})
    ET.SubElement(button,"text").text=label
    ET.SubElement(button,"action",{"function":"page"}).text=destination
    page.append(button)
    return button

def detail_button(page, key):
    helpname=key+"_help"
    # Exact same visual position/size/color/typography as R22d4c main Help.
    button=ET.Element("button")
    ET.SubElement(button,"placement",BUTTON.copy())
    ET.SubElement(button,"fill",{"color":BLUE})
    ET.SubElement(button,"font",{"resource":"font_s","color":WHITE})
    ET.SubElement(button,"text").text="Help"
    ET.SubElement(button,"action",{"function":"page"}).text=helpname
    page.insert(1,button)

def help_page(key):
    info=CONTENT[key]
    page=ET.Element("page",{"name":key+"_help"})
    ET.SubElement(page,"template",{"name":"page"})
    add_text(page,info["title"],81,192,font="font_l")
    for index,(heading,description) in enumerate(info["entries"]):
        assert len(description)<=74,(key,index,description)
        ypos=322+index*60
        if heading:
            add_text(page,heading,82,ypos,color="%accent_color%")
        add_text(page,description,578,ypos,color="#d0dce9")
    add_button(page,"Back to Package",
               {"x":"1455","y":"1053","w":"375","h":"69"},
               key,color="#264e7c")
    back=ET.SubElement(page,"action")
    ET.SubElement(back,"touch",{"key":"back"})
    ET.SubElement(back,"action",{"function":"page"}).text=key
    return page

def update_fragment(path,key):
    tree=ET.parse(path)
    root=tree.getroot()
    assert root.tag=="future_toolkit_pages"
    pages=root.findall("page")
    assert pages and pages[0].get("name")==key,(path,[p.get("name") for p in pages])
    assert len(pages) in (1,2)
    if len(pages)==2:
        assert pages[1].get("name")==key+"_help"
        root.remove(pages[1])
    for b in pages[0].findall("button"):
        if b.findtext("text")=="Help":
            assert b.find("action").text==key+"_help"
            pages[0].remove(b)
    detail_button(pages[0],key)
    root.append(help_page(key))
    ET.indent(tree,space="  ")
    buf=io.BytesIO()
    tree.write(buf,encoding="utf-8",xml_declaration=True)
    if not path.exists() or path.read_bytes()!=buf.getvalue():
        path.write_bytes(buf.getvalue())
    print("PACKAGE_HELP_UP_TO_DATE",key,path.name)

def existing_fragments():
    root=ET.Element("future_toolkit_pages")
    root.append(ET.Comment("Add the matching Help button to each existing package Open page; R22d4c remains frozen."))
    for key in ("xoom_network","xoom_toolkit_details_poc"):
        detail=ET.SubElement(root,"help_button_injection",{"page":key})
        detail_button(detail,key)
        root.append(help_page(key))
    tree=ET.ElementTree(root)
    ET.indent(tree,space="  ")
    buf=io.BytesIO()
    tree.write(buf,encoding="utf-8",xml_declaration=True)
    if EXISTING.exists():
        assert EXISTING.read_bytes()==buf.getvalue(), "Refusing unexpected changes to staged help"
    else:
        EXISTING.write_bytes(buf.getvalue())
    print("EXISTING_PACKAGE_HELP_UP_TO_DATE",EXISTING.name)

if __name__=="__main__":
    update_fragment(TIME,"xoom_toolkit_details_time_sync")
    update_fragment(LOGS,"xoom_toolkit_details_log_collector")
    update_fragment(DIAG,"xoom_toolkit_details_diag")
    update_fragment(INSPECT,"xoom_toolkit_details_partition_inspector")
    existing_fragments()
