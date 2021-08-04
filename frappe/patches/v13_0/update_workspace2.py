import frappe
import json
from frappe import _

def execute():
	frappe.reload_doc('desk', 'doctype', 'workspace', force=True)
	order_by = "pin_to_top desc, pin_to_bottom asc, name asc"
	for seq, wspace in enumerate(frappe.get_all('Workspace', order_by=order_by)):
		doc = frappe.get_doc('Workspace', wspace.name)
		content = create_content(doc)
		update_wspace(doc, seq, content)
	frappe.db.commit()

def create_content(doc):
	content = []
	if doc.onboarding:
		content.append({"type":"onboarding","data":{"onboarding_name":doc.onboarding,"col":12,"pt":0,"pr":0,"pb":0,"pl":0}})
	if doc.charts:
		invalid_links = []
		for c in doc.charts:
			if c.get_invalid_links()[0]:
				invalid_links.append(c)
			else:
				content.append({"type":"chart","data":{"chart_name":c.label,"col":12,"pt":0,"pr":0,"pb":0,"pl":0}})
		for l in invalid_links:
			del doc.charts[doc.charts.index(l)]
	if doc.shortcuts:
		invalid_links = []
		if doc.charts:
			content.append({"type":"spacer","data":{"col":12,"pt":0,"pr":0,"pb":0,"pl":0}})
		content.append({"type":"header","data":{"text":doc.shortcuts_label or _("Your Shortcuts"),"level":4,"col":12,"pt":0,"pr":0,"pb":0,"pl":0}})
		for s in doc.shortcuts:
			if s.get_invalid_links()[0]:
				invalid_links.append(s)
			else:
				content.append({"type":"shortcut","data":{"shortcut_name":s.label,"col":4,"pt":0,"pr":0,"pb":0,"pl":0}})
		for l in invalid_links:
			del doc.shortcuts[doc.shortcuts.index(l)]
	if doc.links:
		invalid_links = []
		content.append({"type":"spacer","data":{"col":12,"pt":0,"pr":0,"pb":0,"pl":0}})
		content.append({"type":"header","data":{"text":doc.cards_label or _("Reports & Masters"),"level":4,"col":12,"pt":0,"pr":0,"pb":0,"pl":0}})
		for l in doc.links:
			if l.type == 'Card Break':
				content.append({"type":"card","data":{"card_name":l.label,"col":4,"pt":0,"pr":0,"pb":0,"pl":0}})
			if l.get_invalid_links()[0]:
				invalid_links.append(l)
		for l in invalid_links:
			del doc.links[doc.links.index(l)]
	return content

def update_wspace(doc, seq, content):
	if not doc.is_standard and not doc.public:
		doc.sequence_id = seq + 1
		doc.content = json.dumps(content)
		doc.public = 0
		doc.title = doc.extends
		doc.extends = ''
		doc.category = ''
		doc.onboarding = ''
		doc.extends_another_page = 0
		doc.is_default = 0
		doc.is_standard = 0
		doc.developer_mode_only = 0
		doc.disable_user_customization = 0
		doc.pin_to_top = 0
		doc.pin_to_bottom = 0
		doc.hide_custom = 0
		doc.save(ignore_permissions=True)