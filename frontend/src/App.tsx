import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from '@/components/layout/AppLayout';
import DashboardPage from '@/pages/DashboardPage';
import ScannerPage from '@/pages/ScannerPage';
import HistoryPage from '@/pages/HistoryPage';
import ReportPage from '@/pages/ReportPage';
import ModelComparisonPage from '@/pages/ModelComparisonPage';
import SettingsPage from '@/pages/SettingsPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="scanner" element={<ScannerPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="report/:id" element={<ReportPage />} />
          <Route path="models" element={<ModelComparisonPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
