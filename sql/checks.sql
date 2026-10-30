-- name: duplicate_customer_emails
SELECT email, COUNT(*) AS n FROM customers GROUP BY email HAVING COUNT(*) > 1;

-- name: orphan_bookings
SELECT b.id FROM bookings b LEFT JOIN customers c ON c.id = b.customer_id WHERE c.id IS NULL;

-- name: refunds_exceeding_booking
SELECT r.id, r.amount_usd, b.amount_usd AS booked FROM refunds r JOIN bookings b ON b.id = r.booking_id
WHERE r.amount_usd > b.amount_usd;

-- name: full_refunds_outside_policy_window
SELECT r.id, julianday(r.refunded_on) - julianday(b.booked_on) AS days FROM refunds r JOIN bookings b ON b.id = r.booking_id
WHERE r.kind = 'full' AND julianday(r.refunded_on) - julianday(b.booked_on) > 14;

-- name: refund_total_reconciliation
SELECT (SELECT SUM(amount_usd) FROM refunds) AS refunds_total,
       (SELECT SUM(r.amount_usd) FROM refunds r JOIN bookings b ON b.id = r.booking_id) AS matched_total;
