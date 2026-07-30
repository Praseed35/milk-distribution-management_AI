import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../providers/AuthProvider";
import { navigation, filterNavByRole } from "../../config/permissions";

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [expandedMenus, setExpandedMenus] = useState<Set<string>>(new Set());
  const { user } = useAuth();
  const location = useLocation();

  if (!user) return null;

  const navItems = filterNavByRole(navigation, user.role);

  function toggleMenu(label: string) {
    setExpandedMenus((prev) => {
      const next = new Set(prev);
      if (next.has(label)) next.delete(label);
      else next.add(label);
      return next;
    });
  }

  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + "/");

  return (
    <aside
      className={`bg-slate-800 text-white flex flex-col transition-all duration-200 ${
        collapsed ? "w-16" : "w-64"
      }`}
    >
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        {!collapsed && <span className="font-bold text-lg">ERP</span>}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-slate-400 hover:text-white p-1"
        >
          {collapsed ? "→" : "←"}
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto py-2">
        {navItems.map((item) => {
          if (item.children) {
            const open = expandedMenus.has(item.label);
            return (
              <div key={item.label}>
                <button
                  onClick={() => toggleMenu(item.label)}
                  className="w-full text-left px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 flex items-center justify-between"
                >
                  {!collapsed && <span>{item.label}</span>}
                  {!collapsed && <span>{open ? "▼" : "▶"}</span>}
                </button>
                {open && !collapsed && (
                  <div>
                    {item.children.map((child) => (
                      <Link
                        key={child.path}
                        to={child.path}
                        className={`block pl-8 pr-4 py-2 text-sm ${
                          isActive(child.path)
                            ? "bg-indigo-600 text-white"
                            : "text-slate-400 hover:bg-slate-700"
                        }`}
                      >
                        {child.label}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            );
          }
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`block px-4 py-2 text-sm ${
                isActive(item.path)
                  ? "bg-indigo-600 text-white"
                  : "text-slate-300 hover:bg-slate-700"
              }`}
            >
              {!collapsed && item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
