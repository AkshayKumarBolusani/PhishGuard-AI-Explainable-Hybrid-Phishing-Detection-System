import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { History, Search, Download, Star, Trash2, ExternalLink } from 'lucide-react';
import { historyAPI, scanAPI } from '@/services/api';
import { formatDate, classificationColor } from '@/lib/utils';
import PageHeader from '@/components/ui/PageHeader';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import EmptyState from '@/components/ui/EmptyState';
import ClassificationBadge from '@/components/ui/ClassificationBadge';
import type { ScanListItem } from '@/types';

const FILTERS = [
  { value: '', label: 'All' },
  { value: 'safe', label: 'Safe' },
  { value: 'suspicious', label: 'Suspicious' },
  { value: 'phishing', label: 'Phishing' },
];

export default function HistoryPage() {
  const [items, setItems] = useState<ScanListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await historyAPI.getHistory({
        page,
        page_size: 15,
        search: search || undefined,
        classification: filter || undefined,
      });
      setItems(res.data.data.items);
      setTotal(res.data.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, filter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  };

  const handleDelete = async (id: string) => {
    try {
      await scanAPI.deleteScan(id);
      fetchHistory();
    } catch (err) {
      console.error(err);
    }
  };

  const handleFavorite = async (id: string) => {
    try {
      await scanAPI.toggleFavorite(id);
      fetchHistory();
    } catch (err) {
      console.error(err);
    }
  };

  const handleExport = async (format: string) => {
    try {
      const res = await historyAPI.exportHistory(format);
      const blob = new Blob([res.data], { type: format === 'csv' ? 'text/csv' : 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `phishguard_export.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
    }
  };

  const totalPages = Math.ceil(total / 15);

  return (
    <div className="page-stack">
      <PageHeader
        title="Scan history"
        subtitle={`${total} scan${total !== 1 ? 's' : ''} recorded`}
        actions={
          <div className="flex items-center gap-2">
            <button type="button" onClick={() => handleExport('csv')} className="btn-ghost">
              <Download className="w-4 h-4" strokeWidth={1.75} /> CSV
            </button>
            <button type="button" onClick={() => handleExport('json')} className="btn-ghost">
              <Download className="w-4 h-4" strokeWidth={1.75} /> JSON
            </button>
          </div>
        }
      />

      <div className="flex flex-col lg:flex-row gap-4">
        <form onSubmit={handleSearch} className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)] pointer-events-none" strokeWidth={1.75} />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search subject, sender, or body..."
            className="field pl-10"
            aria-label="Search scans"
          />
        </form>
        <div className="flex flex-wrap gap-2">
          {FILTERS.map((f) => (
            <button
              key={f.value}
              type="button"
              onClick={() => { setFilter(f.value); setPage(1); }}
              className={`chip ${filter === f.value ? 'chip-active' : ''}`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <div className="surface overflow-hidden">
        {loading ? (
          <LoadingSpinner label="Loading history..." />
        ) : items.length === 0 ? (
          <EmptyState
            icon={History}
            title="No scans found"
            description={search || filter ? 'Try adjusting your search or filters.' : 'Run your first email scan to build your threat history.'}
            actionLabel="Go to scanner"
            actionTo="/scanner"
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="table-pro">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Sender</th>
                  <th>Classification</th>
                  <th>Risk</th>
                  <th>Date</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr
                    key={item.id}
                    className="cursor-pointer group"
                    onClick={() => navigate(`/report/${item.id}`)}
                  >
                    <td className="max-w-[260px]">
                      <p className="text-[var(--color-text)] font-medium truncate group-hover:text-[var(--color-accent-hover)] transition-colors">{item.subject}</p>
                    </td>
                    <td className="max-w-[200px]">
                      <p className="text-[var(--color-text-muted)] truncate text-sm mono">{item.sender}</p>
                    </td>
                    <td><ClassificationBadge classification={item.classification} size="sm" /></td>
                    <td>
                      <span
                        className="text-sm font-semibold tabular-nums"
                        style={{ color: classificationColor(item.risk_score > 50 ? 'phishing' : item.risk_score > 25 ? 'suspicious' : 'safe') }}
                      >
                        {item.risk_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="text-[var(--color-text-muted)] text-sm whitespace-nowrap tabular-nums">{formatDate(item.created_at)}</td>
                    <td>
                      <div className="flex items-center justify-end gap-1" onClick={(e) => e.stopPropagation()}>
                        <button type="button" onClick={() => navigate(`/report/${item.id}`)} className="btn-icon hover:text-[var(--color-accent)]" aria-label="View report">
                          <ExternalLink className="w-4 h-4" strokeWidth={1.75} />
                        </button>
                        <button type="button" onClick={() => handleFavorite(item.id)} className={`btn-icon ${item.is_favorite ? 'text-[#fbbf24]' : 'hover:text-[#fbbf24]'}`} aria-label="Toggle favorite">
                          <Star className={`w-4 h-4 ${item.is_favorite ? 'fill-current' : ''}`} strokeWidth={1.75} />
                        </button>
                        <button type="button" onClick={() => handleDelete(item.id)} className="btn-icon hover:text-[#f87171]" aria-label="Delete scan">
                          <Trash2 className="w-4 h-4" strokeWidth={1.75} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4 pt-2">
          <button type="button" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="btn-ghost disabled:opacity-30">
            Previous
          </button>
          <span className="text-sm text-[var(--color-text-secondary)] tabular-nums">Page {page} of {totalPages}</span>
          <button type="button" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="btn-ghost disabled:opacity-30">
            Next
          </button>
        </div>
      )}
    </div>
  );
}
