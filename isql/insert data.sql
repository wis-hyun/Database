-- Supplier 데이터 삽입
INSERT INTO Supplier (`S_shap`, `SNAME`, `STATUS`, `CITY`) VALUES
('S1', 'Smith', 20, 'London'),
('S2', 'Jones', 10, 'Paris'),
('S3', 'Blake', 30, 'Paris'),
('S4', 'Clark', 20, 'London'),
('S5', 'Adams', 30, 'Athens');

-- Part 데이터 삽입
INSERT INTO Part (`P_shap`, `PNAME`, `COLOR`, `WEIGHT`, `CITY`) VALUES
('P1', 'Nut', 'Red', 12, 'London'),
('P2', 'Bolt', 'Green', 17, 'Paris'),
('P3', 'Screw', 'Blue', 17, 'Rome'),
('P4', 'Screw', 'Red', 14, 'London'),
('P5', 'Cam', 'Blue', 12, 'Paris'),
('P6', 'Cog', 'Red', 19, 'London');

-- Project 데이터 삽입
INSERT INTO Project (`J_shap`, `JNAME`, `CITY`) VALUES
('J1', 'Sorter', 'Paris'),
('J2', 'Punch', 'Rome'),
('J3', 'Reader', 'Athens'),
('J4', 'Console', 'Athens'),
('J5', 'Collator', 'London'),
('J6', 'Terminal', 'Oslo'),
('J7', 'Tape', 'London');

-- SPJ 데이터 삽입
INSERT INTO SPJ (`S_shap`, `P_shap`, `J_shap`, `QTY`) VALUES
('S1', 'P1', 'J1', 200),
('S1', 'P1', 'J4', 700),
('S2', 'P3', 'J1', 400),
('S2', 'P3', 'J2', 200),
('S2', 'P3', 'J3', 200),
('S2', 'P3', 'J4', 500),
('S2', 'P3', 'J5', 600),
('S2', 'P3', 'J6', 400),
('S2', 'P3', 'J7', 800),
('S2', 'P5', 'J2', 100),
('S3', 'P3', 'J1', 200),
('S3', 'P4', 'J2', 500),
('S4', 'P6', 'J3', 300),
('S4', 'P6', 'J7', 300),
('S5', 'P2', 'J2', 200),
('S5', 'P2', 'J4', 100),
('S5', 'P5', 'J5', 500),
('S5', 'P5', 'J7', 100),
('S5', 'P6', 'J2', 200),
('S5', 'P1', 'J4', 100),
('S5', 'P3', 'J4', 200),
('S5', 'P4', 'J4', 800),
('S5', 'P5', 'J4', 400),
('S5', 'P6', 'J4', 500);