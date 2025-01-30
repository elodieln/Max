// src/lib/supabase.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://wpvyfnqdaxsyhgkhefxi.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwdnlmbnFkYXhzeWhna2hlZnhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzgyNDc2ODEsImV4cCI6MjA1MzgyMzY4MX0.4sCl1gMSmMmCeDuo4Lr5EEZCuWi5aHPK1jQTh5CwwuM'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

