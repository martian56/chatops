import { Link } from 'react-router-dom';
import { Server, Settings, LogOut } from 'lucide-react';
import { Button } from '../ui/button';
import { useAuth } from '../../hooks/useAuth';

export const Navbar = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link to="/servers" className="flex items-center gap-2 font-semibold">
            <Server className="h-5 w-5" />
            <span>ChatOps</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link
              to="/servers"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Servers
            </Link>
            <Link
              to="/alerts"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Alerts
            </Link>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">{user?.email}</span>
          <Link to="/settings">
            <Button variant="ghost" size="icon">
              <Settings className="h-4 w-4" />
            </Button>
          </Link>
          <Button variant="ghost" size="icon" onClick={handleLogout}>
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </nav>
  );
};

