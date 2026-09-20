# SupportDesk implementation plan

SupportDesk already has a working Django API, MongoDB connection, React frontend, ticketing, knowledge-base articles, activity logging and AI-assisted replies. The goal is to turn that base into a real support product rather than replace it.

## Phase 1 — Accounts, portals and access control

- Customer self-registration and login
- Link each customer login to one customer record
- Customer can only see and reply to their own tickets
- Customer never sees internal notes
- Agent can see assigned tickets and the unassigned queue
- Admin and supervisor retain full queue visibility
- Role-specific dashboard and navigation
- Admin can create/deactivate team accounts and change roles
- Customer profile page
- Published knowledge base becomes the customer help center
- Backend authorization mirrors the UI rules

## Phase 2 — Support workflow

- Assignment controls for admins and supervisors
- Ticket ownership history
- Better status workflow and reopen rules
- Canned replies / macros
- Tags and categories management
- Customer detail page with ticket timeline
- Agent workload view
- Supervisor queue view
- Bulk ticket actions
- Stronger search and pagination

## Phase 3 — Communication and files

- Ticket attachments with file validation
- SMTP notifications for ticket creation and replies
- Password reset by email
- Optional email verification
- Agent notification when a customer replies
- Customer notification when a ticket changes status
- Email delivery state stored in activity history

## Phase 4 — SLA, automation and reporting

- SLA policies by priority
- First-response and resolution targets
- Breach / near-breach indicators
- Auto-assignment rules
- Automatic priority/category suggestions
- Saved filters
- Agent response-time reporting
- Resolution-time reporting
- Volume by source/category/priority
- CSV export

## Phase 5 — Production hardening

- API tests for every role boundary
- Browser-level workflow tests
- Rate limiting for login and public registration
- Better validation and error states
- Audit-log coverage for sensitive actions
- Security headers and deployment checks
- Responsive QA
- Seed/demo environment
- README and architecture documentation

## Role matrix

| Capability | Customer | Agent | Supervisor | Admin |
| --- | --- | --- | --- | --- |
| Register themselves | Yes | No | No | No |
| View own tickets | Yes | — | — | — |
| View assigned/unassigned queue | No | Yes | Yes | Yes |
| View all tickets | No | No | Yes | Yes |
| Reply to customer | No | Yes | Yes | Yes |
| Reply on own ticket | Yes | — | — | — |
| Internal notes | No | Yes | Yes | Yes |
| AI reply suggestions | No | Yes | Yes | Yes |
| Manage knowledge base | No | No | Yes | Yes |
| View activity audit | No | No | Yes | Yes |
| Create staff accounts | No | No | No | Yes |
| Change staff roles | No | No | No | Yes |

Phase 1 is implemented first because every later workflow depends on trustworthy identity and authorization.
