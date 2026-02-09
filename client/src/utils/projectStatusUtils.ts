/**
 * Utility functions for project status calculations.
 */

export type ProjectHealthStatus = 'green' | 'yellow' | 'red'

export interface ProjectStatusFields {
  is_on_scope: boolean | null
  is_on_time: boolean | null
  is_on_budget: boolean | null
}

/**
 * Calculate the overall project health status based on the three boolean fields.
 * 
 * @param status - Project status fields
 * @returns 'green' if 3 are true, 'yellow' if 2 are true, 'red' if 0-1 are true
 */
export function calculateProjectHealthStatus(status: ProjectStatusFields | null): ProjectHealthStatus {
  if (!status) {
    return 'red' // No status = red flag
  }

  const greenCount = [
    status.is_on_scope,
    status.is_on_time,
    status.is_on_budget
  ].filter(value => value === true).length

  if (greenCount >= 3) {
    return 'green'
  } else if (greenCount === 2) {
    return 'yellow'
  } else {
    return 'red' // 0 or 1 green
  }
}

/**
 * Get a human-readable label for the health status.
 */
export function getHealthStatusLabel(status: ProjectHealthStatus): string {
  switch (status) {
    case 'green':
      return 'Healthy'
    case 'yellow':
      return 'At Risk'
    case 'red':
      return 'Critical'
    default:
      return 'Unknown'
  }
}

/**
 * Get a description for the health status.
 */
export function getHealthStatusDescription(status: ProjectHealthStatus): string {
  switch (status) {
    case 'green':
      return 'All three status indicators are positive'
    case 'yellow':
      return 'Two out of three status indicators are positive'
    case 'red':
      return 'One or zero status indicators are positive'
    default:
      return 'Status unknown'
  }
}
