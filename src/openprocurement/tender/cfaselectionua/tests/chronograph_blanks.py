# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta
from iso8601 import parse_date

from openprocurement.api.utils import get_now
from openprocurement.tender.cfaselectionua.constants import BOT_NAME
from openprocurement.tender.cfaselectionua.tests.base import test_author, test_agreement


# TenderSwitchTenderingResourceTest


def switch_to_tendering(self):
    self.set_status("draft.pending")

    self.app.authorization = ("Basic", (BOT_NAME, ""))
    agreement = deepcopy(test_agreement)
    agreement["contracts"][1]["unitPrices"][0]["value"]["amount"] = (
        agreement["contracts"][2]["unitPrices"][0]["value"]["amount"] * 2
    )
    agreement_id = self.initial_data["agreements"][0]["id"]
    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

    self.set_status("active.enquiries", start_end="end")

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")


def switch_to_tendering_by_tenderPeriod_startDate(self):
    self.set_status("active.enquiries")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    contracts = response.json["data"]["agreements"][0]["contracts"]
    for contract in contracts:
        self.assertIn("value", contract)
        self.assertEqual(
            contract["value"]["amount"],
            self.initial_data["items"][0]["quantity"] * contract["unitPrices"][0]["value"]["amount"],
        )

    # testing min 1 day delta before patching from active.enquiries to active.tendering by chronograph
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.enquiries")  # not changed

    # time travel  change enquiryPeriod.endDate && tenderPeriod.startDate <= they are equal
    self.set_status("active.enquiries", start_end="end")

    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.tendering")  # now changed


# TenderSwitchQualificationResourceTest


def switch_to_qualification(self):
    self.set_status("active.tendering", start_end="end")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertEqual(len(response.json["data"]["awards"]), 1)


# TenderSwitchAuctionResourceTest


def switch_to_auction(self):
    self.set_status("active.tendering", start_end="end")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")


# TenderSwitchUnsuccessfulResourceTest


def switch_to_unsuccessful(self):
    self.set_status("active.tendering", start_end="end")
    response = self.check_chronograph()
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    if self.initial_lots:
        self.assertEqual(set([i["status"] for i in response.json["data"]["lots"]]), set(["unsuccessful"]))


# TenderAuctionPeriodResourceTest


def set_auction_period(self):
    self.set_status("active.enquiries", start_end="end")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    if self.initial_lots:
        item = response.json["data"]["lots"][0]
    else:
        item = response.json["data"]
    self.assertIn("auctionPeriod", item)
    self.assertIn("shouldStartAfter", item["auctionPeriod"])
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertIn("T00:00:00+", item["auctionPeriod"]["shouldStartAfter"])
    self.assertEqual(
        parse_date(response.json["data"]["next_check"]), parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    if self.initial_lots:
        response = self.check_chronograph(
            {"data": {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}]}}
        )
        item = response.json["data"]["lots"][0]
    else:
        response = self.check_chronograph({"data": {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}})
        item = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(item["auctionPeriod"]["startDate"], "9999-01-01T00:00:00+00:00")

    if self.initial_lots:
        response = self.check_chronograph({"data": {"lots": [{"auctionPeriod": {"startDate": None}}]}})
        item = response.json["data"]["lots"][0]
    else:
        response = self.check_chronograph({"data": {"auctionPeriod": {"startDate": None}}})
        item = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("startDate", item["auctionPeriod"])


def reset_auction_period(self):
    self.set_status("active.enquiries", start_end="end")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    if self.initial_lots:
        item = response.json["data"]["lots"][0]
    else:
        item = response.json["data"]
    self.assertIn("auctionPeriod", item)
    self.assertIn("shouldStartAfter", item["auctionPeriod"])
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertEqual(
        parse_date(response.json["data"]["next_check"]),
        parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    if self.initial_lots:
        response = self.check_chronograph({"data": {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
        item = response.json["data"]["lots"][0]
    else:
        response = self.check_chronograph({"data": {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
        item = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertIn("9999-01-01T00:00:00", item["auctionPeriod"]["startDate"])

    self.set_status("active.tendering", start_end="end")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")
    item = response.json["data"]["lots"][0] if self.initial_lots else response.json["data"]
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])

    if self.initial_lots:
        response = self.check_chronograph({"data": {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
        item = response.json["data"]["lots"][0]
    else:
        response = self.check_chronograph({"data": {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
        item = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertIn("9999-01-01T00:00:00", item["auctionPeriod"]["startDate"])
    self.assertIn("9999-01-01T00:00:00", response.json["data"]["next_check"])

    now = get_now().isoformat()
    tender = self.db.get(self.tender_id)
    if self.initial_lots:
        tender["lots"][0]["auctionPeriod"]["startDate"] = now
    else:
        tender["auctionPeriod"]["startDate"] = now
    self.db.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")
    item = response.json["data"]["lots"][0] if self.initial_lots else response.json["data"]
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertGreater(
        parse_date(response.json["data"]["next_check"]),
        parse_date(item["auctionPeriod"]["startDate"])
    )
    self.assertEqual(response.json["data"]["next_check"], self.db.get(self.tender_id)["next_check"])

    if self.initial_lots:
        response = self.check_chronograph(
            {"data": {"lots": [{"auctionPeriod": {"startDate": response.json["data"]["tenderPeriod"]["endDate"]}}]}}
        )
        item = response.json["data"]["lots"][0]
    else:
        response = self.check_chronograph(
            {"data": {"auctionPeriod": {"startDate": response.json["data"]["tenderPeriod"]["endDate"]}}}
        )
        item = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertNotIn("9999-01-01T00:00:00", item["auctionPeriod"]["startDate"])
    self.assertGreater(
        parse_date(response.json["data"]["next_check"]),
        parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    tender = self.db.get(self.tender_id)
    self.assertGreater(tender["next_check"], response.json["data"]["tenderPeriod"]["endDate"])
    tender["tenderPeriod"]["endDate"] = tender["tenderPeriod"]["startDate"]
    if self.initial_lots:
        tender["lots"][0]["auctionPeriod"]["startDate"] = tender["tenderPeriod"]["startDate"]
    else:
        tender["auctionPeriod"]["startDate"] = tender["tenderPeriod"]["startDate"]
    self.db.save(tender)

    response = self.check_chronograph()
    if self.initial_lots:
        item = response.json["data"]["lots"][0]
    else:
        item = response.json["data"]
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertNotIn("next_check", response.json["data"])
    self.assertNotIn("next_check", self.db.get(self.tender_id))
    shouldStartAfter = item["auctionPeriod"]["shouldStartAfter"]

    response = self.check_chronograph()
    if self.initial_lots:
        item = response.json["data"]["lots"][0]
    else:
        item = response.json["data"]
    self.assertEqual(item["auctionPeriod"]["shouldStartAfter"], shouldStartAfter)
    self.assertNotIn("next_check", response.json["data"])

    if self.initial_lots:
        response = self.check_chronograph({"data": {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
        item = response.json["data"]["lots"][0]
    else:
        response = self.check_chronograph({"data": {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
        item = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertIn("9999-01-01T00:00:00", item["auctionPeriod"]["startDate"])
    self.assertIn("9999-01-01T00:00:00", response.json["data"]["next_check"])


# TenderComplaintSwitchResourceTest


def switch_to_ignored_on_complete(self):
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": {
                "title": "complaint title",
                "description": "complaint description",
                "author": test_author,
                "status": "claim",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    self.set_status("active.tendering", "end")
    self.check_chronograph()
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertEqual(response.json["data"]["complaints"][0]["status"], "ignored")


def switch_from_pending_to_ignored(self):
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": {
                "title": "complaint title",
                "description": "complaint description",
                "author": test_author,
                "status": "claim",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.db.get(self.tender_id)
    tender["complaints"][0]["status"] = "pending"
    self.db.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["complaints"][0]["status"], "ignored")


def switch_from_pending(self):
    for status in ["invalid", "resolved", "declined"]:
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": {
                    "title": "complaint title",
                    "description": "complaint description",
                    "author": test_author,
                    "status": "claim",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.db.get(self.tender_id)
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        tender["complaints"][index]["status"] = "pending"
        tender["complaints"][index]["resolutionType"] = status
        tender["complaints"][index]["dateEscalated"] = "2017-06-01"
    self.db.save(tender)

    response = self.check_chronograph()
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        self.assertEqual(response.json["data"]["complaints"][index]["status"], status)


def switch_to_complaint(self):
    for status in ["invalid", "resolved", "declined"]:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": {
                    "title": "complaint title",
                    "description": "complaint description",
                    "author": test_author,
                    "status": "claim",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")
        complaint = response.json["data"]
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
            {"data": {"status": "answered", "resolution": status * 4, "resolutionType": status}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "answered")
        self.assertEqual(response.json["data"]["resolutionType"], status)

        tender = self.db.get(self.tender_id)
        tender["complaints"][-1]["dateAnswered"] = (
            get_now() - timedelta(days=1 if "procurementMethodDetails" in tender else 4)
        ).isoformat()
        self.db.save(tender)

        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["complaints"][-1]["status"], status)


# TenderAwardComplaintSwitchResourceTest


def award_switch_to_ignored_on_complete(self):
    token = self.initial_bids_tokens.values()[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {
            "data": {
                "title": "complaint title",
                "description": "complaint description",
                "author": test_author,
                "status": "claim",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]

    tender = self.db.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active", "value": {"valueAddedTaxIncluded": False}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["awards"][0]["complaints"][0]["status"], "ignored")


def award_switch_from_pending_to_ignored(self):
    token = self.initial_bids_tokens.values()[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {
            "data": {
                "title": "complaint title",
                "description": "complaint description",
                "author": test_author,
                "status": "claim",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.db.get(self.tender_id)
    tender["awards"][0]["complaints"][0]["status"] = "pending"
    self.db.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["awards"][0]["complaints"][0]["status"], "ignored")


def award_switch_from_pending(self):
    token = self.initial_bids_tokens.values()[0]
    for status in ["invalid", "resolved", "declined"]:
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
            {
                "data": {
                    "title": "complaint title",
                    "description": "complaint description",
                    "author": test_author,
                    "status": "claim",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.db.get(self.tender_id)
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        tender["awards"][0]["complaints"][index]["status"] = "pending"
        tender["awards"][0]["complaints"][index]["resolutionType"] = status
        tender["awards"][0]["complaints"][index]["dateEscalated"] = "2017-06-01"
    self.db.save(tender)

    response = self.check_chronograph()
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        self.assertEqual(response.json["data"]["awards"][0]["complaints"][index]["status"], status)


def award_switch_to_complaint(self):
    token = self.initial_bids_tokens.values()[0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    for status in ["invalid", "resolved", "declined"]:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
            {
                "data": {
                    "title": "complaint title",
                    "description": "complaint description",
                    "author": test_author,
                    "status": "claim",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")
        complaint = response.json["data"]

        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], self.tender_token
            ),
            {"data": {"status": "answered", "resolution": status * 4, "resolutionType": status}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "answered")
        self.assertEqual(response.json["data"]["resolutionType"], status)

        tender = self.db.get(self.tender_id)
        tender["awards"][0]["complaints"][-1]["dateAnswered"] = (
            get_now() - timedelta(days=1 if "procurementMethodDetails" in tender else 4)
        ).isoformat()
        self.db.save(tender)

        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["awards"][0]["complaints"][-1]["status"], status)
