-- Synthetic booking data with a few planted problems for the checks to find.
CREATE TABLE customers (id INTEGER PRIMARY KEY, email TEXT NOT NULL);
CREATE TABLE bookings (id INTEGER PRIMARY KEY, customer_id INTEGER, booked_on DATE, amount_usd NUMERIC);
CREATE TABLE refunds (id INTEGER PRIMARY KEY, booking_id INTEGER, refunded_on DATE, amount_usd NUMERIC, kind TEXT);

INSERT INTO customers VALUES (1, 'ana@example.com'), (2, 'luis@example.com'), (3, 'ana@example.com');
INSERT INTO bookings VALUES
  (10, 1, '2026-09-01', 300), (11, 2, '2026-09-03', 450), (12, 9, '2026-09-05', 120), (13, 3, '2026-09-10', 200);
INSERT INTO refunds VALUES
  (100, 10, '2026-09-08', 300, 'full'),    -- inside the 14-day window
  (101, 11, '2026-10-01', 450, 'full'),    -- 28 days later: should have been travel credit
  (102, 13, '2026-09-12', 250, 'full');    -- refund larger than the booking
