==================
Dominican Republic
==================

.. |DGII| replace:: :abbr:`DGII (Dirección General de Impuestos Internos)`
.. |EDI| replace:: :abbr:`EDI (Electronic Data Interchange)`
.. |ECF| replace:: :abbr:`ECF (Comprobante Fiscal Electrónico)`
.. |eNCF| replace:: :abbr:`eNCF (Número de Comprobante Fiscal Electrónico)`
.. |RNC| replace:: :abbr:`RNC (Registro Nacional del Contribuyente)`
.. |ITBIS| replace:: :abbr:`ITBIS (Impuesto a la Transferencia de Bienes Industrializados y Servicios)`

.. _localizations/dominican-republic/modules:

Modules
=======

The following modules related to the Dominican Republic localization are available:

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Name
     - Technical name
     - Description
   * - :guilabel:`Dominican Republic - Accounting`
     - `l10n_do`
     - The default :doc:`fiscal localization package <../fiscal_localizations>`. It adds accounting
       characteristics for the Dominican Republic localization, which represent the minimum
       configuration required for a company to operate in the Dominican Republic according to the
       |DGII| guidelines.
   * - :guilabel:`Dominican Republic - Accounting EDI`
     - `l10n_do_edi`
     - Includes all the technical and functional requirements to generate and validate
       :doc:`Electronic Fiscal Receipts <../accounting/customer_invoices/electronic_invoicing>`
       (|ECF|) with XML files, electronic numbers (eNCF), and digital signatures, based on the
       technical documentation published by the |DGII|.
   * - :guilabel:`Dominican Republic - Accounting Reports`
     - `l10n_do_reports`
     - Provides financial reports tailored to the Dominican Republic's regulatory requirements.
   * - :guilabel:`Dominican Republic - Checks Layout`
     - `l10n_do_check_printing`
     - Enables the printing of checks formatted for Dominican Republic banking standards.

.. note::
   The localization's core modules are installed automatically with the localization. The rest can
   be manually :doc:`installed </applications/general/apps_modules>`.

.. _localizations/dominican-republic/loc-review:

Localization overview
=====================

The Dominican Republic localization package ensures compliance with Dominican Republic fiscal and
accounting regulations. It includes tools for managing taxes, fiscal positions, reporting, and a
predefined chart of accounts tailored to the Dominican Republic’s standards.

The Dominican Republic localization package provides the following key features to ensure compliance
with local fiscal and accounting regulations:

- :ref:`Chart of accounts <localizations/dominican-republic/chart-of-accounts>`: a predefined
  structure tailored to Dominican Republic accounting standards.
- :ref:`Taxes <localizations/dominican-republic/taxes>`: pre-configured tax rates, including
  standard VAT, zero-rated, and exempt options.
- :doc:`Reporting <../accounting/reporting>`
- :ref:`E-invoicing (Infile) <localizations/dominican-republic/electronic-invoicing>`: integration
  for electronic invoicing in line with the Dominican Republic's government requirements.

.. _localizations/dominican-republic/chart-of-accounts:

Chart of accounts
-----------------

The :doc:`chart of accounts <../accounting/get_started/chart_of_accounts>` is installed by default
as part of the data set included with the localization module. Accounts are automatically mapped to
taxes, default accounts payable, and default accounts receivable.

Use the :ref:`predefined structure <chart-of-account/create>` or create and delete accounts
according to the company's needs.

.. _localizations/dominican-republic/taxes:

Taxes
-----

As part of the Dominican Republic localization module, :doc:`taxes <../accounting/taxes>` are
automatically created with their configuration and related financial accounts. The main taxes
available include:

- :guilabel:`18% ITBIS`: Standard VAT rate applied to most goods and services (sales and purchases).
- :guilabel:`16% ITBIS`: Reduced |ITBIS| rate applicable to certain goods.
- :guilabel:`0% ITBIS`: Zero-rated |ITBIS| for certain transactions.
- :guilabel:`ITBIS Exempt`: For goods and services fully exempt from |ITBIS|.
- :guilabel:`Withholding taxes`: |ITBIS| and ISR withholdings depending on |DGII| regulations.
- :guilabel:`10% Propina`: Legal tip (propina) applicable to hospitality and restaurant services.

Multi-currency
~~~~~~~~~~~~~~

The Dominican Republic's official currency is the Dominican Peso (DOP), symbolized as RD$.
:doc:`Additional foreign currencies <../accounting/get_started/multi_currency>` can also be enabled
and configured, as needed.

.. _localizations/dominican-republic/company-contacts:

Company and contacts
====================

To use all the features of this fiscal localization, the following fields are required on the
:doc:`company record </applications/general/companies>`:

- :guilabel:`Company Name`
- :guilabel:`Address`, including the :guilabel:`Street`, :guilabel:`City`, :guilabel:`State`,
  :guilabel:`ZIP`, and :guilabel:`Country`
- :guilabel:`RNC`: Enter the company's *Registro Nacional del Contribuyente* number, which is
  required for all electronic fiscal documents.

The same configuration applies to the relevant Dominican Republic :doc:`contact
<../../essentials/contacts>` form to issue a valid |ECF| to a business customer.

.. note::
   If the customer's RNC is not available, it is still possible to generate an :guilabel:`E32 -
   Electronic Consumer Invoice` (*Factura de Consumo Electrónica*).

.. _localizations/dominican-republic/electronic-invoicing:

Electronic invoicing with Infile
================================

The following documents are supported:

- :guilabel:`E31 - Electronic Tax Credit Invoice` (*Factura de Crédito Fiscal Electrónica*)
- :guilabel:`E32 - Electronic Consumer Invoice` (*Factura de Consumo Electrónica*)
- :guilabel:`E33 - Electronic Debit Note` (*Nota de Débito Electrónica*)
- :guilabel:`E34 - Electronic Credit Note` (*Nota de Crédito Electrónica*)

.. note::
   An `Infile <https://infile.com/republica-dominicana>`_ account is required to generate and submit
   electronic fiscal receipts to the |DGII|.

.. _localizations/dominican-republic/e-invoice-configuration:

Configuration
-------------

.. note::
   Make sure to :ref:`install <general/install>` the :guilabel:`Dominican Republic - Accounting EDI`
   (`l10n_do_edi`) module.

Odoo connects with Infile to generate and submit electronic fiscal documents to the |DGII| for
validation. To ensure proper validation and the official |eNCF| assignment, configure this
connection before issuing documents:

#. Sign a service agreement directly with `Infile <https://infile.com/republica-dominicana>`_ to
   enable as Electronic Invoicer and receive Infile credentials.
#. Go to :menuselection:`Accounting --> Configuration --> Settings`, scroll down to the
   :guilabel:`Dominican Republic Electronic Invoicing` section.
#. Select the :guilabel:`Web Service Environment`, either :guilabel:`Demo`, :guilabel:`Test`, or
   :guilabel:`Production`.
#. Enter the :guilabel:`Infile Credentials`:

   - :guilabel:`Username`
   - :guilabel:`Password`
   - :guilabel:`Security Key`
   - :guilabel:`Llave`

#. Click :guilabel:`Save`.

.. tip::
   - The :guilabel:`Infile Credentials` are provided by Infile and are required for both the
     :guilabel:`Test` and :guilabel:`Production` environments. If they are not available, contact
     Infile support.
   - The :guilabel:`Demo` environment is intended for local testing only and does not generate legal
     documents, official |eNCF| sequences, or submit documents to the |DGII|. No Infile account or
     credentials are needed to use it.

.. _localizations/dominican-republic/e-invoice-journals:

Journals
~~~~~~~~

For electronic invoicing flows, :doc:`journals <../accounting/get_started/journals>` must be
configured with the following settings:

- :guilabel:`Type`: Sales
- :guilabel:`Use Documents?`: Enabled, to enforce |ECF| document type selection on invoices.

.. note::
   :ref:`Document types <localizations/dominican-republic/e-invoice-document-types>` that are not
   yet supported in Odoo, but available from the Infile portal, can still be registered in journals
   without |EDI| configurations set.

.. _localizations/dominican-republic/e-invoice-document-types:

Document types
~~~~~~~~~~~~~~

The Dominican Republic localization defines the following electronic document types, accessible
under :menuselection:`Accounting --> Configuration --> Document Types`:

.. list-table::
   :header-rows: 1
   :widths: 10 30 20 20

   * - Code
     - Name
     - Document Code Prefix
     - Internal Type
   * - 31
     - Electronic Tax Credit Invoice
     - E31
     - Invoices
   * - 32
     - Electronic Consumer Invoice
     - E32
     - Invoices
   * - 33
     - Electronic Debit Note
     - E33
     - Debit Notes
   * - 34
     - Electronic Credit Note
     - E34
     - Credit Notes

.. _localizations/dominican-republic/e-invoice-document-range:

Document ranges
***************

Each :ref:`document type <localizations/dominican-republic/e-invoice-document-types>` requires an
associated :guilabel:`Document Range`, which defines the valid sequence of |eNCF| numbers, including
starting and ending sequence numbers and an expiration date.

To configure a document range to a document type, go to :menuselection:`Accounting --> Configuration
--> Document Types`, click the relevant document type in the :guilabel:`Document Types` list view,
and select a :guilabel:`Document Range` in the :guilabel:`Dominican Republic Authorized Range`
field.

To create a new :guilabel:`Document Range`, select :guilabel:`Search more ...` in the
:guilabel:`Dominican Republic Authorized Range` field. Then, click :guilabel:`Create New` and set
the following fields:

- :guilabel:`Starting Sequence Number`: first number in the authorized range
- :guilabel:`Ending Sequence Number`: last number in the authorized range
- :guilabel:`Expiration Date`: date through which the sequence range is valid (e.g., December
  31 of the current fiscal year)

.. important::
   - Document ranges must be requested from the |DGII| and configured before issuing electronic
     fiscal documents.
   - If a sequence is exhausted or expired, new ranges must be requested from the |DGII|.

.. _localizations/dominican-republic/customer-invoices:

Customer invoices
-----------------

Once the :ref:`configuration <localizations/dominican-republic/e-invoice-configuration>` is
complete, electronic fiscal documents can be :ref:`created
<localizations/dominican-republic/invoice-creation>` and :ref:`sent
<localizations/dominican-republic/invoice-sending>` to the |DGII|.

.. _localizations/dominican-republic/invoice-creation:

Invoice creation
~~~~~~~~~~~~~~~~

When :ref:`creating a customer invoice <accounting/invoice/creation>` for electronic submission via
Infile, complete the following Dominican Republic-specific fields before clicking
:guilabel:`Confirm`:

- :guilabel:`Customer`: Select a customer :ref:`contact
  <localizations/dominican-republic/company-contacts>`.
- :guilabel:`Journal`: Select an :ref:`|EDI| configured sales journal
  <localizations/dominican-republic/e-invoice-journals>`. Two additional fields appear:

  - :guilabel:`Document Type`: Select the |ECF| :ref:`type
    <localizations/dominican-republic/e-invoice-document-types>` to generate (auto-suggested based on
    customer profile).
  - :guilabel:`Income Type`: Select the income classification code that applies to the transaction
    (e.g., :guilabel:`Operational Income`).

.. note::
   Once confirmed, the invoice is assigned an |eNCF| number (format `E310000000001`), where the
   first two digits (`31`) represent the document type code, and the remaining digits form the
   sequential number within the authorized range.

.. _localizations/dominican-republic/invoice-sending:

Invoice sending
~~~~~~~~~~~~~~~

To send the invoice, follow these steps:

#. Click :guilabel:`Send`.
#. In the :guilabel:`Send` window, enable these options:

   - :guilabel:`DGII`: To submit the |ECF| XML to the |DGII| through Infile's web service.
   - :guilabel:`by Email`: To send the validated document to the customer's email.

#. Click :guilabel:`Send`.

The following actions occur:

- The |ECF| XML file is generated.
- The XML file is processed and signed synchronously by Infile and submitted to the |DGII|.
- The |ECF| PDF and XML files are attached to the customer's email and available in the chatter for
  download.
- To review the status assigned by the |DGII|, click :guilabel:`Request DGII Status`.

.. tip::
   If errors are reported in the chatter, reset the invoice to draft, make the necessary
   corrections, and resend it.

.. _localizations/dominican-republic/debit-credit-notes:

Debit and credit notes
----------------------

To send a debit or credit note to the |DGII|, first create the
:ref:`debit note <accounting/credit_notes/issue-debit-note>` or
:ref:`credit note <accounting/credit_notes/issue-credit-note>` from the original invoice using
the :guilabel:`Debit Note` or :guilabel:`Credit Note` buttons, respectively.

In the :guilabel:`Debit Note` or :guilabel:`Credit Note` window, select a :guilabel:`Modification
Code`.
Then, follow the same :ref:`sending process <localizations/dominican-republic/invoice-sending>` as
for invoices.
