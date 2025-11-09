export const HomePage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center px-4">
        <div className="mb-8">
          <div className="w-24 h-24 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <div className="w-16 h-16 bg-indigo-600 rounded-full animate-pulse"></div>
          </div>
        </div>

        <h1 className="text-5xl font-bold text-white mb-4">Coming Soon</h1>

        <p className="text-lg text-slate-500 mb-8 max-w-md">
          We're working hard to bring you something amazing. Stay tuned!
        </p>

        <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <span>Under construction</span>
        </div>
      </div>
    </div>
  );
};
