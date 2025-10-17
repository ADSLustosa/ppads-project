import http from 'k6/http'; import { check, sleep } from 'k6';
export const options = { vus: 25, duration: '1m' };
export default function () {
  const r = http.post(`${__ENV.API_URL}/pix/send`,
    JSON.stringify({ key: __ENV.DEST_PIX, amount: 10 }),
    { headers:{ 'Content-Type':'application/json', 'Authorization':`Bearer ${__ENV.TOKEN}` }});
  check(r, { 'ok': res => [200,201].includes(res.status) });
  sleep(1);
}