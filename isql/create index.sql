CREATE INDEX idx_supplier ON Supplier(S_shap);
CREATE INDEX idx_part ON Part(P_shap);
CREATE INDEX idx_project ON Project(J_shap);
CREATE INDEX idx_spj ON SPJ(S_shap, P_shap, J_shap);
