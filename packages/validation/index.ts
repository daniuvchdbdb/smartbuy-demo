import { z } from 'zod';
export const targetPriceSchema = z.object({ variant_id:z.number().int().positive(), target_price:z.number().positive() });
