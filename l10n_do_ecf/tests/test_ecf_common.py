# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo.tests import tagged
from .common import TestL10nDoCommon
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tools import misc
import os
import base64


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestL10nDoEcfCommon(TestL10nDoCommon):

    @classmethod
    @AccountTestInvoicingCommon.setup_country('do')
    def setUpClass(cls):
        super().setUpClass()
        file_path = os.path.join(
            "l10n_do_ecf", "tests", "certificates", "test.p12"
        )
        file_content = misc.file_open(file_path, mode="rb").read()
        # Crear certificado de firma electrónica válido
        cls.certificate = (
            cls.env["ecf.settings"]
            .sudo()
            .create(
                {
                    "name": "Test",
                    "ce_p12_name": "test.p12",
                    "ce_p12_pin": "Adel0312",
                    "ce_p12_file": base64.b64encode(file_content),
                    "company_id": cls.company.id,
                },
            )
        )

        cls.company.write(
            {
                "l10n_do_ecf_issuer": True,
            }
        )

        journal_vals = {
            "l10n_latam_use_documents": True,
        }
        cls.journal_sale.write(
            journal_vals
        )
        cls.journal_purchase.write(
            journal_vals
        )
        cls.partner_contact.write(
            {
                "l10n_do_dgii_tax_payer_type": "taxpayer",
                "street": "SN",
                "email": "adelbeltran03@gmail.com",
            }
        )
        cls.company.write(
            {
                "ecf_config": cls.certificate.id,
            }
        )
        cls.FiscalSequence = cls.env["account.fiscal.sequence"].with_company(cls.company).sudo()
        fs_e31 = cls.FiscalSequence.create({"name": "E31",
                                            "fiscal_type_id": cls.env.ref(
                                                 "l10n_do_accounting.ecf_fiscal_client").id,
                                            "sequence_start": 3600,
                                            "sequence_end": 5000,
                                            })
        fs_e31._action_confirm()
        cls.fs_e31 = fs_e31
        fs_e32 = cls.FiscalSequence.create({"name": "E32",
                                            "fiscal_type_id": cls.env.ref(
                                                 "l10n_do_accounting.ecf_consumer_supplier").id,
                                            "sequence_start": 3600,
                                            "sequence_end": 5000,
                                            })
        fs_e32._action_confirm()
        cls.fs_e32 = fs_e32
        fs_e33 = cls.FiscalSequence.create({"name": "E33",
                                            "fiscal_type_id": cls.env.ref(
                                                "l10n_do_accounting.ecf_debit_note_client").id,
                                            "sequence_start": 3600,
                                            "sequence_end": 5000,
                                            })
        fs_e33._action_confirm()
        cls.fs_e34 = fs_e33
        fs_e34 = cls.FiscalSequence.create({"name": "E34",
                                            "fiscal_type_id": cls.env.ref(
                                                "l10n_do_accounting.ecf_credit_note_client").id,
                                            "sequence_start": 3600,
                                            "sequence_end": 5000,
                                            })
        fs_e34._action_confirm()
        cls.fs_e34 = fs_e34
        fs_e41 = cls.FiscalSequence.create({"name": "E41",
                                            "fiscal_type_id": cls.env.ref(
                                                "l10n_do_accounting.ecf_informal_supplier").id,
                                            "sequence_start": 3600,
                                            "sequence_end": 5000,
                                            })
        fs_e41._action_confirm()
        cls.fs_e41 = fs_e41
