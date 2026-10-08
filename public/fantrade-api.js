/**
 * Fantrade Backend REST API Client
 * Connects the UI to the real PostgreSQL Exchange Engine, eliminating synthetic mock data.
 */
(function(window) {
  const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? (window.location.port === '3001' ? '' : 'http://localhost:3001')
    : '';

  let isApiOnline = false;

  async function request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    // Use active demo session or token
    const token = localStorage.getItem('fantrade_auth_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const res = await fetch(url, { ...options, headers });
      const data = await res.json().catch(() => null);

      if (!res.ok) {
        const errorMsg = data?.error?.message || `Request failed with status ${res.status}`;
        const err = new Error(errorMsg);
        err.code = data?.error?.code || 'API_ERROR';
        err.status = res.status;
        throw err;
      }

      isApiOnline = true;
      return data;
    } catch (err) {
      if (err.message && err.message.includes('Failed to fetch')) {
        isApiOnline = false;
        console.warn('[FantradeAPI] Backend server unreachable at ' + url);
      }
      throw err;
    }
  }

  // Keep the same request key if a write's response is lost. A retry can
  // retrieve its receipt rather than buying, swapping or staking twice.
  async function transactionRequest(endpoint, body, prefix, explicitKey) {
    const token = localStorage.getItem('fantrade_auth_token') || '';
    let account = 0;
    for (const char of token) account = ((account * 31) + char.charCodeAt(0)) >>> 0;
    const storage = 'ft_pending_write_' + account;
    const signature = endpoint + ':' + JSON.stringify(body);
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem(storage) || '{}'); } catch {}
    const key = saved[signature] || explicitKey || prefix + '-' + Date.now() + '-' + Math.random().toString(36).slice(2);
    saved[signature] = key;
    localStorage.setItem(storage, JSON.stringify(saved));
    try {
      const result = await request(endpoint, { method: 'POST', headers: { 'Idempotency-Key': key }, body: JSON.stringify(body) });
      delete saved[signature]; localStorage.setItem(storage, JSON.stringify(saved));
      return result;
    } catch (error) {
      if (error.status >= 400 && error.status < 500) { delete saved[signature]; localStorage.setItem(storage, JSON.stringify(saved)); }
      throw error;
    }
  }

  const FantradeAPI = {
    isOnline: () => isApiOnline,

    async checkHealth() {
      try {
        const res = await request('/health');
        isApiOnline = res?.status === 'ok';
        return isApiOnline;
      } catch {
        isApiOnline = false;
        return false;
      }
    },

    async getAssets(params = {}) {
      const q = new URLSearchParams(params).toString();
      return request(`/api/assets${q ? '?' + q : ''}`);
    },

    async getAsset(symbol) {
      return request(`/api/assets/${encodeURIComponent(symbol)}`);
    },

    async getOrderBook(symbol) {
      return request(`/api/markets/${encodeURIComponent(symbol)}/order-book`);
    },

    async getTrades(symbol, limit = 50) {
      return request(`/api/markets/${encodeURIComponent(symbol)}/trades?limit=${limit}`);
    },

    async getMarketStats(symbol) {
      return request(`/api/markets/${encodeURIComponent(symbol)}/stats`);
    },

    async getPriceHistory(symbol, interval = '1m') {
      return request(`/api/markets/${encodeURIComponent(symbol)}/price-history?interval=${interval}`);
    },

    async getWallet() {
      return request('/api/wallet');
    },

    async getPortfolio() {
      return request('/api/portfolio');
    },

    async getOrders(status) {
      const q = status ? `?status=${status}` : '';
      return request(`/api/orders${q}`);
    },

    async placeOrder({ assetSymbol, side, quantity, limitPrice, type = 'LIMIT', timeInForce = 'GTC' }) {
      return transactionRequest('/api/orders', {assetSymbol,side:side.toUpperCase(),type,quantity,limitPrice,timeInForce}, 'ord');
    },

    async cancelOrder(orderId) {
      return request(`/api/orders/${encodeURIComponent(orderId)}/cancel`, {
        method: 'POST',
      });
    },

    async swapAssets({ fromSymbol, toSymbol, shares }) {
      return transactionRequest('/api/swaps', {fromSymbol,toSymbol,shares}, 'swp');
    },

    // FanPlay Engine Methods (Prompt 4)
    async getFanPlayMarkets() {
      return request('/api/fanplay/markets');
    },

    async getFanPlayMatches() {
      return request('/api/fanplay/matches');
    },

    async getFanPlayOptions(assetIdOrParams, matchId, marketTier) {
      let params;
      if (typeof assetIdOrParams === 'object' && assetIdOrParams !== null) {
        params = assetIdOrParams;
      } else {
        params = {};
        if (assetIdOrParams) params.assetId = assetIdOrParams;
        if (matchId) params.matchId = matchId;
        if (marketTier) params.marketTier = marketTier;
      }
      const q = new URLSearchParams(params).toString();
      return request(`/api/fanplay/options${q ? '?' + q : ''}`);
    },

    async getFanPlayEligibleAssets() {
      return request('/api/fanplay/eligible-assets');
    },

    async previewFanPlay(payload) {
      return request('/api/fanplay/preview', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },

    async activateFanPlay(payload) {
      return transactionRequest('/api/fanplay/activate', payload, 'fp', payload.idempotencyKey);
    },

    async simulateFanPlay(id){return request('/api/fanplay/'+encodeURIComponent(id)+'/simulate',{method:'POST'});},
    async getFanPlays(status) {
      const q = status ? `?status=${status}` : '';
      return request(`/api/fanplay${q}`);
    },

    async getFanPlay(id) {
      return request(`/api/fanplay/${encodeURIComponent(id)}`);
    },

    async cancelFanPlay(id) {
      return request(`/api/fanplay/${encodeURIComponent(id)}/cancel`, {
        method: 'POST',
      });
    },

    async getFanPlayLive(id) {
      return request(`/api/fanplay/${encodeURIComponent(id)}/live`);
    },

    async settleFanPlay(id, forceFinal = false) {
      return request(`/api/fanplay/${encodeURIComponent(id)}/settle`, {
        method: 'POST',
        body: JSON.stringify({ forceFinal }),
      });
    },
  };

  window.FantradeAPI = FantradeAPI;

  // Shared application state restores the selected account service after auth is ready.
})(window);
